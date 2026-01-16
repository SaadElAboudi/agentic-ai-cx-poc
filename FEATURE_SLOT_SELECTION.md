# Amélioration PoC : Sélection de Créneaux par le Client

## Vue d'ensemble

Le PoC a été amélioré pour permettre au client de **choisir parmi plusieurs créneaux disponibles** avant de confirmer le rebooking, au lieu de booker automatiquement le premier créneau.

## Problème Résolu

**Avant :**
- L'agent rebookait automatiquement le premier créneau disponible
- Le client n'avait pas son mot à dire
- Moins d'autonomie du client

**Après :**
- L'agent présente les créneaux disponibles au client
- Le client choisit celui qui lui convient
- Meilleure expérience utilisateur

## Architecture Améliorée

### Flux en 2 Étapes

```
ÉTAPE 1: Initial Request
┌────────────────────────────────────────────┐
│ Client: "Je veux reprogrammer mon RDV"     │
├────────────────────────────────────────────┤
│ POST /agentic-cx                           │
│ {                                          │
│   "customer_id": "123",                    │
│   "message": "Je veux reprogrammer..."     │
│ }                                          │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│ Agent Reasoning                            │
├────────────────────────────────────────────┤
│ ✓ Détecte: missed_appointment_rebook      │
│ ✓ Vérifie éligibilité: OK                 │
│ ✓ Récupère créneaux: 3 disponibles        │
│ ✓ Decision: PRESENT_OPTIONS (nouveau!)    │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│ Response avec Créneaux                     │
├────────────────────────────────────────────┤
│ {                                          │
│   "status": "awaiting_client_choice",     │
│   "available_slots": [                     │
│     {                                      │
│       "slot_id": "slot_20250116_1400",    │
│       "date": "2025-01-16",               │
│       "time": "14:00",                    │
│       "service_type": "consultation"      │
│     },                                     │
│     { ... 2 autres créneaux ... }         │
│   ],                                       │
│   "session_id": "session_123_..."         │
│ }                                          │
└────────────────────────────────────────────┘

ÉTAPE 2: Client Confirmation
┌────────────────────────────────────────────┐
│ Client sélectionne: slot_20250116_1400    │
├────────────────────────────────────────────┤
│ POST /agentic-cx/confirm-slot              │
│ {                                          │
│   "customer_id": "123",                    │
│   "slot_id": "slot_20250116_1400",        │
│   "session_id": "session_123_..."         │
│ }                                          │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│ Agent Book le Créneau                      │
├────────────────────────────────────────────┤
│ ✓ Valide le slot                          │
│ ✓ Enregistre le RDV                       │
│ ✓ Envoie confirmation (email + SMS)       │
│ Decision: AUTOMATE                        │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│ Response de Confirmation                   │
├────────────────────────────────────────────┤
│ {                                          │
│   "status": "resolved",                    │
│   "appointment_details": { ... },         │
│   "confirmation_sent": { ... }            │
│ }                                          │
└────────────────────────────────────────────┘
```

## Modifications Techniques

### 1. **Méthode `_execute_rebooking()` Améliorée**
   
**Paramètre nouveau :** `slot_id: str = None`

**Comportements :**
- Si `slot_id` est `None` (initial request) :
  - Récupère les créneaux disponibles
  - Retourne `status: "awaiting_client_choice"`
  - Inclut `session_id` et `available_slots`

- Si `slot_id` est fourni (confirmation) :
  - Rebook immédiatement le créneau choisi
  - Retourne `status: "resolved"`
  - Inclut les détails du RDV

**Code :**
```python
def _execute_rebooking(self, customer_id: str, customer_data: dict, slot_id: str = None) -> tuple:
    # Si slot_id est None → retourner les créneaux
    if slot_id is None:
        return actions, {
            "session_id": session_id,
            "available_slots": slots_for_client,
            "message": "Please choose one of the available slots"
        }, "awaiting_client_choice"
    
    # Si slot_id est fourni → booker le créneau
    else:
        rebook_result = self.cx_system.rebook_appointment(customer_id, slot_id)
        return actions, {...}, "resolved"
```

### 2. **Nouvelle Méthode : `confirm_appointment_booking()`**

Gère la 2ème étape (confirmation du client).

```python
def confirm_appointment_booking(
    self, customer_id: str, slot_id: str, session_id: str
) -> Dict:
    """
    Confirm and finalize appointment booking when customer selects a slot.
    """
    # Récupère contexte client
    customer_data = self.cx_system.get_customer(customer_id)
    
    # Exécute le rebooking avec le slot choisi
    actions_taken, result, status = self._execute_rebooking(
        customer_id, customer_data, slot_id=slot_id
    )
    
    # Retourne réponse confirmée
    return response
```

### 3. **Nouveau Modèle Pydantic : `SlotSelectionRequest`**

```python
class SlotSelectionRequest(BaseModel):
    customer_id: str
    slot_id: str
    session_id: str
```

### 4. **Nouveaux Endpoints API**

#### Endpoint 1: POST `/agentic-cx` (existant, amélioré)
**Comportement :**
- Si intent = "missed_appointment_rebook" et eligible
- Retourne `status: "awaiting_client_choice"` au lieu de "resolved"
- Inclut liste des `available_slots`
- Génère `session_id`

**Response exemple :**
```json
{
  "intent": "missed_appointment_rebook",
  "goal": "Offer available appointment slots",
  "decision": "Customer is eligible, showing available options",
  "decision_type": "AUTOMATE",
  "status": "awaiting_client_choice",
  "available_slots": [
    {
      "slot_id": "slot_20250116_1400",
      "date": "2025-01-16",
      "time": "14:00",
      "service_type": "consultation"
    },
    {
      "slot_id": "slot_20250116_1530",
      "date": "2025-01-16",
      "time": "15:30",
      "service_type": "consultation"
    }
  ],
  "session_id": "session_123_1705424400",
  "confidence": 0.95,
  "explanation": "I found available appointment slots. Please select the time that works best for you."
}
```

#### Endpoint 2: POST `/agentic-cx/confirm-slot` (NOUVEAU)
**Paramètres :**
- `customer_id`: ID du client
- `slot_id`: ID du créneau sélectionné
- `session_id`: ID de session pour validation

**Response exemple :**
```json
{
  "intent": "missed_appointment_rebook",
  "goal": "Confirm and finalize the selected appointment",
  "decision": "Booking confirmed for the selected time slot",
  "decision_type": "AUTOMATE",
  "status": "resolved",
  "actions_taken": [
    "check_eligibility",
    "find_available_slots",
    "rebook_appointment",
    "send_confirmation"
  ],
  "appointment_details": {
    "appointment_id": "apt_20250116_1400",
    "service_type": "consultation",
    "scheduled_date": "2025-01-16T14:00:00Z",
    "status": "confirmed"
  },
  "confirmation_sent": {
    "method": "email + SMS",
    "recipient": {
      "email": "customer@example.com",
      "phone": "+33-600-000000"
    }
  },
  "confidence": 0.95,
  "explanation": "Your appointment has been confirmed for the selected time slot. You'll receive a confirmation via email and SMS."
}
```

## Exemple d'Utilisation Complète

### Step 1: Client demande le rebooking
```bash
curl -X POST "http://localhost:8000/agentic-cx" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "123",
    "message": "Je veux reprogrammer mon rendez-vous manqué"
  }'
```

**Response :**
```json
{
  "status": "awaiting_client_choice",
  "available_slots": [
    {"slot_id": "slot_1400", "date": "2025-01-16", "time": "14:00"},
    {"slot_id": "slot_1530", "date": "2025-01-16", "time": "15:30"},
    {"slot_id": "slot_1700", "date": "2025-01-17", "time": "17:00"}
  ],
  "session_id": "session_123_1705424400"
}
```

### Step 2: Client sélectionne un créneau
```bash
curl -X POST "http://localhost:8000/agentic-cx/confirm-slot" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "123",
    "slot_id": "slot_1530",
    "session_id": "session_123_1705424400"
  }'
```

**Response :**
```json
{
  "status": "resolved",
  "appointment_details": {
    "appointment_id": "apt_20250116_1530",
    "scheduled_date": "2025-01-16T15:30:00Z"
  },
  "explanation": "Your appointment has been confirmed for 15:30. Confirmation sent to your email and phone."
}
```

## Avantages de Cette Approche

✅ **Meilleure UX** : Client choisit le créneau qui lui convient
✅ **Moins d'escalade** : Pas besoin d'appeler un agent pour "demander des horaires"
✅ **Plus autonome** : Client décide vraiment
✅ **Flexible** : Adapté pour chat, IVR, email, SMS
✅ **Scalable** : Même pattern pour d'autres intents (annulation, modification, etc.)
✅ **Traçable** : `session_id` lie les 2 requêtes

## Options Futures

1. **Session Storage** : Persister les sessions en Redis/Database pour timeout et validation
2. **Notification** : Envoyer les créneaux par SMS/email avant de demander le choix
3. **Feedback** : Tracker quel créneau est choisi vs affiché (optimisation)
4. **Multi-language** : Adapter textes des créneaux à la langue du client
5. **Preferences** : Apprendre les horaires préférés du client (matin vs soir)

## Backward Compatibility

✅ Les anciens clients continuent à fonctionner
✅ Pour redevenir "full auto", il suffit de toujours appeler `/confirm-slot` avec le premier créneau

---

**Date d'implémentation :** 16 janvier 2026
**Status :** ✅ Implémenté et testé
