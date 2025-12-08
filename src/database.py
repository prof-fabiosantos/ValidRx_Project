# Copyright 2025 ValidRx Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from sqlalchemy import create_engine, Column, String, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de Conexão
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==============================================================================
# MODELOS (TABELAS)
# ==============================================================================

class Medicamento(Base):
    __tablename__ = "medicamentos"

    id = Column(String, primary_key=True, index=True)
    nome = Column(String)
    principio_ativo = Column(String)
    classe_terapeutica = Column(String)
    familias_alergia = Column(JSON)      # Postgres nativo JSON
    concentracao_mg_ml = Column(Float)
    min_idade_meses = Column(Integer)
    dose_max_diaria_adulto_mg = Column(Float)
    contra_indicacoes = Column(JSON)     # Postgres nativo JSON
    vias_permitidas = Column(JSON)       # Postgres nativo JSON

    # Relacionamento 1-para-1 com Pediatria
    pediatria = relationship(
        "Pediatria",
        uselist=False,
        back_populates="medicamento",
        cascade="all, delete-orphan"
    )


class Pediatria(Base):
    __tablename__ = "pediatria"

    medicamento_id = Column(String, ForeignKey("medicamentos.id"), primary_key=True)
    modo = Column(String)  # 'mg_kg_dose' ou 'mg_kg_dia'
    min = Column(Float)
    max = Column(Float)
    teto_dose = Column(Float)

    medicamento = relationship("Medicamento", back_populates="pediatria")


class Interacao(Base):
    __tablename__ = "interacoes"

    id = Column(Integer, primary_key=True, index=True)
    substancia_a = Column(String)
    substancia_b = Column(String)
    nivel = Column(String)  # ALTO, MEDIO
    mensagem = Column(String)


# ==============================================================================
# GERENCIADOR DE BANCO DE DADOS
# ==============================================================================

class DatabaseManager:
    def __init__(self):
        # Cria as tabelas se não existirem
        Base.metadata.create_all(bind=engine)
        self.seed_data_if_empty()

    def get_db(self):
        """
        Retorna uma sessão do banco.
        O caller é responsável por chamar db.close().
        """
        return SessionLocal()

    def seed_data_if_empty(self):
        db = self.get_db()
        try:
            if db.query(Medicamento).count() == 0:
                print("Inicializando banco PostgreSQL com dados de seed...")

                # Adrenalina
                adre = Medicamento(
                    id="MED_ADRE",
                    nome="Adrenalina 1mg/mL",
                    principio_ativo="epinefrina",
                    classe_terapeutica="vasopressor",
                    familias_alergia=[],
                    concentracao_mg_ml=1.0,
                    min_idade_meses=0,
                    dose_max_diaria_adulto_mg=1.0,
                    contra_indicacoes=[],
                    vias_permitidas=["Intramuscular (IM)", "Endovenosa (IV)", "Subcutânea"],
                )
                ped_adre = Pediatria(
                    medicamento_id="MED_ADRE",
                    modo="mg_kg_dose",
                    min=0.01,
                    max=0.01,
                    teto_dose=0.5,
                )

                # Amoxicilina
                amox = Medicamento(
                    id="MED_AMOX",
                    nome="Amoxicilina Susp. 250mg/5ml",
                    principio_ativo="amoxicilina",
                    classe_terapeutica="antibiotico",
                    familias_alergia=["penicilina"],
                    concentracao_mg_ml=50.0,
                    min_idade_meses=0,
                    dose_max_diaria_adulto_mg=3000.0,
                    contra_indicacoes=["mononucleose"],
                    vias_permitidas=["Oral"],
                )
                ped_amox = Pediatria(
                    medicamento_id="MED_AMOX",
                    modo="mg_kg_dia",
                    min=40.0,
                    max=50.0,
                    teto_dose=0,
                )

                # Interação exemplo
                inter = Interacao(
                    substancia_a="varfarina",
                    substancia_b="ibuprofeno",
                    nivel="ALTO",
                    mensagem="🔴 RISCO HEMORRÁGICO.",
                )

                db.add(adre)
                db.add(ped_adre)
                db.add(amox)
                db.add(ped_amox)
                db.add(inter)
                db.commit()
        finally:
            db.close()

    def add_drug(
        self,
        id,
        nome,
        principio,
        classe,
        alergias,
        conc,
        min_idade,
        max_adulto,
        contras,
        vias,
        ped_rule,
    ):
        db = self.get_db()
        try:
            # Upsert (Atualiza se existir, cria se não)
            existing = db.query(Medicamento).filter(Medicamento.id == id).first()
            if existing:
                db.delete(existing)  # Simples estratégia de replace
                db.commit()

            drug = Medicamento(
                id=id,
                nome=nome,
                principio_ativo=principio,
                classe_terapeutica=classe,
                familias_alergia=alergias,
                concentracao_mg_ml=conc,
                min_idade_meses=min_idade,
                dose_max_diaria_adulto_mg=max_adulto,
                contra_indicacoes=contras,
                vias_permitidas=vias,
            )
            db.add(drug)

            if ped_rule:
                ped = Pediatria(
                    medicamento_id=id,
                    modo=ped_rule["modo"],
                    min=ped_rule["min"],
                    max=ped_rule["max"],
                    teto_dose=ped_rule.get("teto_dose", 0),
                )
                db.add(ped)

            db.commit()
        finally:
            db.close()

    def delete_drug(self, drug_id: str) -> bool:
        """
        Remove um medicamento e sua regra pediátrica (se houver).
        Retorna True se removeu, False se não encontrou.
        """
        db = self.get_db()
        try:
            drug = db.query(Medicamento).filter(Medicamento.id == drug_id).first()
            if not drug:
                return False
            db.delete(drug)
            db.commit()
            return True
        finally:
            db.close()

    def add_interaction(self, sub_a, sub_b, nivel, msg):
        db = self.get_db()
        try:
            inter = Interacao(
                substancia_a=sub_a,
                substancia_b=sub_b,
                nivel=nivel,
                mensagem=msg,
            )
            db.add(inter)
            db.commit()
        finally:
            db.close()

    def get_all_drugs_dict(self):
        """
        Converte os Objetos do Banco para Dicionário
        (Para manter compatibilidade com a ClinicalEngine).
        """
        db = self.get_db()
        try:
            drugs = db.query(Medicamento).all()
            drugs_dict = {}

            for d in drugs:
                drug_obj = {
                    "id": d.id,
                    "nome": d.nome,
                    "principio_ativo": d.principio_ativo,
                    "classe_terapeutica": d.classe_terapeutica,
                    "familias_alergia": d.familias_alergia,
                    "concentracao_mg_ml": d.concentracao_mg_ml,
                    "min_idade_meses": d.min_idade_meses,
                    "dose_max_diaria_adulto_mg": d.dose_max_diaria_adulto_mg,
                    "contra_indicacoes": d.contra_indicacoes,
                    "vias_permitidas": d.vias_permitidas,
                    "pediatria": None,
                }
                if d.pediatria:
                    drug_obj["pediatria"] = {
                        "modo": d.pediatria.modo,
                        "min": d.pediatria.min,
                        "max": d.pediatria.max,
                        "teto_dose": d.pediatria.teto_dose,
                    }
                drugs_dict[d.id] = drug_obj

            return drugs_dict
        finally:
            db.close()

    def get_interactions(self):
        db = self.get_db()
        try:
            inters = db.query(Interacao).all()
            return [
                {
                    "pair": {i.substancia_a, i.substancia_b},
                    "level": i.nivel,
                    "msg": i.mensagem,
                }
                for i in inters
            ]
        finally:
            db.close()


