from typing import List, Dict

class ClinicalEngine:
    def __init__(self, drugs_dict, interactions_list):
        self.drugs = drugs_dict
        self.interactions = interactions_list

    def validate(self, patient, prescription):
        alerts = []
        drug = self.drugs.get(prescription['drug_id'])
        if not drug: return [{"type": "WARNING", "msg": f"Medicamento ID {prescription['drug_id']} não encontrado."}]

        # Dados
        weight = patient['weight_kg']
        age_months = patient['age_months']
        conditions = set(patient['conditions'])
        allergies = set(patient['allergies'])
        current_meds = patient['current_meds'] # Lista de IDs
        
        dose_input = prescription['dose_input']
        route = prescription['route']
        freq = prescription['freq_hours']

        # Normalização Dose
        dose_mg = dose_input * drug['concentracao_mg_ml'] if drug['concentracao_mg_ml'] else dose_input

        # --- CAMADA 1: VIA ---
        if route not in drug['vias_permitidas']:
            alerts.append({"type": "BLOCK", "msg": f"⛔ ERRO DE VIA: {drug['nome']} permite apenas {drug['vias_permitidas']}."})
        
        # Regra Fatal Adrenalina
        if "Adrenalina" in drug['nome'] and route == "Endovenosa (IV)" and "parada_cardiaca" not in conditions:
             alerts.append({"type": "BLOCK", "msg": "⛔ ERRO FATAL: Adrenalina IV só permitida em Parada Cardíaca (PCR)."})

        # --- CAMADA 2: IDADE ---
        if age_months < drug['min_idade_meses']:
            alerts.append({"type": "BLOCK", "msg": f"⛔ PROIBIDO PARA IDADE ({age_months} meses)."})

        # --- CAMADA 3: ALERGIAS ---
        match_alg = set(drug['familias_alergia']).intersection(allergies)
        if match_alg: alerts.append({"type": "BLOCK", "msg": f"⛔ ALERGIA DETECTADA: {list(match_alg)}."})

        # --- CAMADA 4: CONTRAINDICAÇÕES ---
        match_cond = set(drug['contra_indicacoes']).intersection(conditions)
        if match_cond: alerts.append({"type": "BLOCK", "msg": f"⛔ CONTRAINDICADO PARA: {list(match_cond)}."})

        # --- CAMADA 5: DUPLICIDADE ---
        existing_classes = {self.drugs[mid]['classe_terapeutica'] for mid in current_meds if mid in self.drugs}
        if drug['classe_terapeutica'] in existing_classes:
            alerts.append({"type": "WARNING", "msg": f"⚠️ DUPLICIDADE: Classe '{drug['classe_terapeutica']}' já em uso."})

        # --- CAMADA 6: INTERAÇÕES ---
        active_principles = {drug['principio_ativo']}
        for mid in current_meds:
            if mid in self.drugs: active_principles.add(self.drugs[mid]['principio_ativo'])
        
        for rule in self.interactions:
            if rule['pair'].issubset(active_principles):
                alerts.append({"type": "BLOCK" if rule['level'] == 'ALTO' else "WARNING", "msg": rule['msg']})

        # --- CAMADA 7: POSOLOGIA ---
        is_child = age_months < 144
        ped_rule = drug.get('pediatria')
        
        if is_child and ped_rule:
            min_dose = round(weight * ped_rule['min'], 4)
            max_dose = round(weight * ped_rule['max'], 4)
            
            raw_val = dose_mg if ped_rule['modo'] == 'mg_kg_dose' else (dose_mg * (24/freq))
            val = round(raw_val, 4)
            
            if ped_rule.get('teto_dose', 0) > 0 and val > ped_rule['teto_dose']:
                alerts.append({"type": "BLOCK", "msg": f"⛔ TETO ABSOLUTO EXCEDIDO: {val}mg > {ped_rule['teto_dose']}mg."})
            elif val > max_dose:
                alerts.append({"type": "BLOCK", "msg": f"⛔ SOBREDOSE TÓXICA: {val}mg > {max_dose}mg."})
            elif val < min_dose:
                alerts.append({"type": "WARNING", "msg": f"⚠️ SUBDOSE: {val}mg < {min_dose}mg."})
        
        elif not is_child:
             val_adulto = round(dose_mg * (24/freq), 4)
             if val_adulto > drug['dose_max_diaria_adulto_mg']:
                 alerts.append({"type": "BLOCK", "msg": "⛔ DOSE MÁXIMA ADULTO EXCEDIDA."})

        return alerts