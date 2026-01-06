#!/usr/bin/env python3
"""
Script to generate an example Excel file for beneficiarios data.
This is a template showing the expected structure.
"""
import pandas as pd
from datetime import datetime, timedelta
import random


def generate_example_data(num_records=10):
    """Generate example beneficiarios data."""
    
    # Sample data
    ciudadanos_ids = [f"CC{str(i).zfill(8)}" for i in range(1000000, 1000000 + num_records)]
    beneficio_ids = [1, 2, 3, 4, 5]  # Different types of benefits
    beneficio_nombres = {
        1: "Subsidio Alimentario",
        2: "Apoyo Educativo",
        3: "Vivienda Social",
        4: "Salud Básica",
        5: "Empleo Temporal"
    }
    estados = ["ACTIVO", "PENDIENTE", "APROBADO"]
    
    data = []
    for ciudadano_id in ciudadanos_ids:
        beneficio_id = random.choice(beneficio_ids)
        fecha = datetime.now() - timedelta(days=random.randint(0, 365))
        
        record = {
            "Ciudadano ID": ciudadano_id,
            "Nombre": f"Ciudadano {ciudadano_id}",
            "Beneficio ID": beneficio_id,
            "Nombre Beneficio": beneficio_nombres[beneficio_id],
            "Fecha Asignacion": fecha.strftime("%Y-%m-%d"),
            "Monto": random.randint(100000, 500000),
            "Estado": random.choice(estados),
            "Observaciones": f"Observación para {ciudadano_id}"
        }
        data.append(record)
    
    return pd.DataFrame(data)


def main():
    """Generate and save example Excel file."""
    print("Generating example beneficiarios data...")
    
    df = generate_example_data(num_records=10)
    
    output_file = "data/ejemplo_beneficiarios.xlsx"
    df.to_excel(output_file, index=False, sheet_name="Beneficiarios")
    
    print(f"Example file created: {output_file}")
    print(f"Number of records: {len(df)}")
    print("\nSample data:")
    print(df.head())


if __name__ == '__main__':
    main()
