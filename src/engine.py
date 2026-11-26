#!/usr/bin/env python3
"""
CobRecon - Motor de Conciliação de Dados
Motor principal para comparação e conciração de registros entre sistemas legados e modernos.
"""

import sqlite3
import pandas as pd
import json
import csv
from typing import List, Dict, Any, Optional, Tuple


class Record:
    """Representa um registro de dados com ID e atributos."""

    def __init__(self, record_id: str, data: Dict[str, Any], source: str):
        self.record_id = record_id
        self.data = data
        self.source = source
        self.is_duplicate = False
        self.divergences: List[Dict[str, Any]] = []

    def __repr__(self):
        return f"Record(id={self.record_id}, source={self.source})"


class CobReconEngine:
    """Motor principal de conciliação de dados do CobRecon."""

    def __init__(self, rules: Optional[Dict] = None):
        self.rules = rules or self._default_rules()
        self.records: List[Record] = []
        self.divergent_records: List[Record] = []
        self.duplicate_records: List[Record] = []

    def _default_rules(self) -> Dict[str, Any]:
        """Regras padrão de conciliação."""
        return {
            "id_field": "id",
            "match_fields": ["name", "value"],
            "tolerance": 0.0,
            "ignore_case": True,
            "allow_duplicates": False,
        }

    def load_from_sqlite(self, db_path: str, table: str = "records") -> None:
        """Carrega registros de um banco de dados SQLite."""
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table}")
            columns = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                record_id = str(row_dict.get(self.rules["id_field"], ""))
                data = row_dict
                source = db_path
                self.records.append(Record(record_id, data, source))
        finally:
            conn.close()

    def load_from_file(self, file_path: str, file_type: str = "auto") -> None:
        """Carrega registros de um arquivo (CSV, JSON, ou COBOL simulado)."""
        if file_type == "auto":
            file_type = file_path.split(".")[-1].lower()

        if file_type == "csv":
            df = pd.read_csv(file_path)
        elif file_type == "json":
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                df = pd.DataFrame(data) if data else pd.DataFrame()
        elif file_type in ("txt", "cobol"):
            df = self._parse_cobol_file(file_path)
        else:
            raise ValueError(f"Tipo de arquivo não suportado: {file_type}")

        if df.empty:
            return

        for _, row in df.iterrows():
            record_id = str(row[self.rules["id_field"]]) if self.rules["id_field"] in row.index else str(row.iloc[0])
            data = row.to_dict()
            source = file_path
            self.records.append(Record(record_id, data, source))

    def _parse_cobol_file(self, file_path: str) -> pd.DataFrame:
        """Parsing simplificado de arquivos COBOL."""
        import pandas as pd

        records = []
        current_record = {}
        id_value = ""
        name_value = ""
        value_value = ""

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Simples parsing de formato COBOL posicional
                if line and not line.startswith('*') and not line.startswith('IDENTIFICATION'):
                    parts = line.split()
                    if len(parts) >= 3:
                        id_value = parts[0] if len(parts[0]) <= 8 else parts[0][:8]
                        name_value = parts[1] if len(parts[1]) <= 20 else parts[1][:20]
                        value_value = parts[2] if len(parts[2]) <= 10 else parts[2][:10]
                        current_record = {
                            "id": id_value,
                            "name": name_value,
                            "value": int(value_value) if value_value.isdigit() else 0
                        }
                        records.append(current_record.copy())

        if records:
            return pd.DataFrame(records)
        return pd.DataFrame(columns=["id", "name", "value"])

    def compare(self, other_records: List[Record]) -> None:
        """Comparar registros atuais com outros registros."""
        for record in other_records:
            self._compare_record(record)

    def _compare_record(self, other: Record) -> None:
        """Comparar um registro individual contra os registros carregados."""
        for self_rec in self.records:
            divergences = self._find_divergences(self_rec, other)
            if divergences:
                other.divergences.extend(divergences)
                if other not in self.divergent_records:
                    self.divergent_records.append(other)

    def _find_divergences(self, rec1: Record, rec2: Record) -> List[Dict[str, Any]]:
        """Encontrar divergências entre dois registros."""
        divergences = []
        for field in self.rules.get("match_fields", ["name", "value"]):
            val1 = str(rec1.data.get(field, "")).lower() if self.rules.get("ignore_case", True) else str(rec1.data.get(field, ""))
            val2 = str(rec2.data.get(field, "")).lower() if self.rules.get("ignore_case", True) else str(rec2.data.get(field, ""))

            if val1 != val2:
                divergences.append({
                    "field": field,
                    "value1": rec1.data.get(field),
                    "value2": rec2.data.get(field),
                    "severity": "high" if field == self.rules.get("id_field") else "medium"
                })
        return divergences

    def detect_duplicates(self) -> List[Record]:
        """Detectar registros duplicados baseados nos campos de match."""
        import pandas as pd

        seen = {}
        duplicates = []

        for record in self.records:
            # Criar uma chave baseada nos campos de match
            key_parts = []
            for field in self.rules.get("match_fields", ["name", "value"]):
                val = str(record.data.get(field, "")).lower() if self.rules.get("ignore_case", True) else str(record.data.get(field, ""))
                key_parts.append(val)
            key = tuple(key_parts)

            if key in seen:
                # Marcar como duplicata
                record.is_duplicate = True
                seen[key].is_duplicate = True
                duplicates.append(record)
                duplicates.append(seen[key])
            else:
                seen[key] = record

        self.duplicate_records = duplicates
        return duplicates

    def reconcile(self) -> Dict[str, Any]:
        """Executar processo completo de conciliação."""
        # 1. Detectar duplicatas
        duplicates = self.detect_duplicates()

        # 2. Gerar relatório
        report = {
            "total_records": len(self.records),
            "unique_records": len([r for r in self.records if not r.is_duplicate]),
            "duplicate_records": len(duplicates),
            "divergent_records": len(self.divergent_records),
            "rules_applied": self.rules,
            "records_summary": [
                {
                    "id": r.record_id,
                    "source": r.source,
                    "is_duplicate": r.is_duplicate,
                    "divergences_count": len(r.divergences),
                }
                for r in self.records
            ],
        }

        return report

    def export_csv(self, file_path: str, fields: Optional[List[str]] = None) -> None:
        """Exportar registros para CSV."""
        fields = fields or self.rules.get("match_fields", ["name", "value"])

        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Escrever cabeçalho
            writer.writerow(["record_id"] + fields)
            # Escrever dados
            for record in self.records:
                row = [record.record_id] + [record.data.get(field, "") for field in fields]
                writer.writerow(row)

    def export_json(self, file_path: str, include: str = "all") -> None:
        """Exportar registros para JSON."""
        data = []
        for record in self.records:
            record_data = {
                "record_id": record.record_id,
                "source": record.source,
                "data": record.data,
                "is_duplicate": record.is_duplicate,
                "divergences": record.divergences,
            }
            data.append(record_data)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    """Função principal para executar o motor CobRecon."""
    import sys

    if len(sys.argv) < 2:
        print("Uso: python engine.py <arquivo_entrada> [regras]")
        print("Tipos suportados: CSV, JSON, TXT (formato COBOL simulado)")
        return

    input_file = sys.argv[1]
    rules_file = sys.argv[2] if len(sys.argv) > 2 else None

    # Inicializar motor
    engine = CobReconEngine()

    # Carregar dados
    try:
        engine.load_from_file(input_file)
        print(f"✓ {len(engine.records)} registros carregados de {input_file}")
    except Exception as e:
        print(f"✗ Erro ao carregar arquivo: {e}")
        return

    # Aplicar regras personalizadas se fornecidas
    if rules_file:
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                custom_rules = json.load(f)
                engine.rules.update(custom_rules)
                print(f"✓ Regras personalizadas aplicadas")
        except Exception as e:
            print(f"⚠ Aviso: Erro ao carregar regras: {e}")

    # Detectar duplicatas
    duplicates = engine.detect_duplicates()
    print(f"✓ {len(duplicates)} registros duplicados detectados")

    # Executar conciliação se houver dados de comparação
    if len(engine.records) > 1:
        report = engine.reconcile()
        print(f"\n=== Relatório de Conciliação ===")
        print(f"Total de registros: {report['total_records']}")
        print(f"Registros únicos: {report['unique_records']}")
        print(f"Registros duplicados: {report['duplicate_records']}")
        print(f"Registros divergentes: {report['divergent_records']}")

        # Exportar resultados
        output_csv = input_file.rsplit(".", 1)[0] + "_reconciled.csv"
        engine.export_csv(output_csv)
        print(f"\n✓ Dados exportados para {output_csv}")

        output_json = input_file.rsplit(".", 1)[0] + "_report.json"
        engine.export_json(output_json)
        print(f"✓ Relatório detalhado exportado para {output_json}")

    print("\n=== CobRecon Concluído ===")


if __name__ == "__main__":
    main()