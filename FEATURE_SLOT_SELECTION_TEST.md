# Test de la Nouvelle Fonctionnalité : Sélection de Créneaux

## Résumé

Le PoC a été amélioré pour permettre aux clients de **choisir parmi plusieurs créneaux disponibles** avant de confirmer le rebooking.

## Avant vs Après

| Aspect | Avant | Après |
|--------|-------|-------|
| **Rebooking** | Auto au 1er créneau | Client choisit le créneau |
| **Endpoints** | 1 endpoint (`/agentic-cx`) | 2 endpoints (+ `/confirm-slot`) |
| **Étapes** | 1 seule | 2 étapes (présentation → confirmation) |
| **Autonomie client** | Limitée | Maximisée |
| **Status flow** | `resolved` | `awaiting_client_choice` → `resolved` |

## Comment Tester Localement

### Étape 1 : Installer et Démarrer

```bash
cd /Users/saadelaboudi/Downloads/app\ howto/agentic_ai_cx_poc

# Si besoin, installer les dépendances
pip install -r requirements.txt

# Démarrer l'application
python3 main.py
```

Vous devriez voir :
```
============================================================
Agentic CX PoC - Starting up
============================================================
API available at: http://localhost:8000
Documentation: http://localhost:8000/docs
============================================================
```

### Étape 2 : Tester le Nouvel Endpoint

**Terminal 1 :** Application running (ne fermer pas)

**Terminal 2 :** Tester les appels API

#### 2a. Première requête - Obtenir les créneaux disponibles

```bash
curl -X POST "http://localhost:8000/agentic-cx" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "123",
    "message": "I missed my appointment, can I reschedule it?"
  }' | jq .
```

**Expected Response :**
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
    },
    {
      "slot_id": "slot_20250117_1000",
      "date": "2025-01-17",
      "time": "10:00",
      "service_type": "consultation"
    }
  ],
  "session_id": "session_123_1705424400",
  "confidence": 0.95,
  "explanation": "I found available appointment slots. Please select the time that works best for you."
}
```

**À noter :**
- ✅ `status: "awaiting_client_choice"` (au lieu de "resolved")
- ✅ `available_slots` : Liste des créneaux
- ✅ `session_id` : ID de session pour validation
- ✅ Pas d'`appointment_details` puisque rien n'a été booké encore

#### 2b. Deuxième requête - Client confirme son choix

Copier les valeurs du `session_id` et d'un `slot_id` de la réponse précédente :

```bash
curl -X POST "http://localhost:8000/agentic-cx/confirm-slot" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "123",
    "slot_id": "slot_20250116_1530",
    "session_id": "session_123_1705424400"
  }' | jq .
```

**Expected Response :**
```json
{
  "intent": "missed_appointment_rebook",
  "goal": "Confirm and finalize the selected appointment",
  "decision": "Booking confirmed for the selected time slot",
  "decision_type": "AUTOMATE",
  "actions_taken": [
    "check_eligibility",
    "find_available_slots",
    "rebook_appointment",
    "send_confirmation"
  ],
  "status": "resolved",
  "confidence": 0.95,
  "appointment_details": {
    "appointment_id": "apt_20250116_1530",
    "service_type": "consultation",
    "scheduled_date": "2025-01-16T15:30:00Z",
    "status": "confirmed"
  },
  "confirmation_sent": {
    "method": "email + SMS",
    "recipient": {
      "email": "alice@example.com",
      "phone": "+1-555-0001"
    }
  },
  "explanation": "Your appointment has been confirmed for the selected time slot. You'll receive a confirmation via email and SMS."
}
```

**À noter :**
- ✅ `status: "resolved"` (confirmation complète)
- ✅ `appointment_details` : Détails du RDV booké
- ✅ `confirmation_sent` : Confirmation envoyée au client
- ✅ Les 4 actions complètes sont exécutées

## Tester via Swagger UI

Une interface interactive est disponible :

```
http://localhost:8000/docs
```

1. Aller à "Swagger UI"
2. Trouver les 2 endpoints :
   - `POST /agentic-cx` (le endpoint original, maintenant amélioré)
   - `POST /agentic-cx/confirm-slot` (le nouveau endpoint)
3. Cliquer sur "Try it out"
4. Remplir les paramètres
5. Cliquer "Execute"

## Scénarios de Test

### Scénario 1 : Happy Path (Client éligible, nombreux créneaux)
```bash
# Request 1
curl -X POST "http://localhost:8000/agentic-cx" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "123", "message": "Can I reschedule?"}'

# Request 2 - Confirmer le 2ème créneau
curl -X POST "http://localhost:8000/agentic-cx/confirm-slot" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "123",
    "slot_id": "slot_20250116_1530",
    "session_id": "..."
  }'
```

### Scénario 2 : Client Non Éligible
```bash
curl -X POST "http://localhost:8000/agentic-cx" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "999",
    "message": "Can I reschedule?"
  }'
```
Expected : `status: "escalated"` avec message d'inéligibilité

### Scénario 3 : Client Inconnu
```bash
curl -X POST "http://localhost:8000/agentic-cx" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "0",
    "message": "Can I reschedule?"
  }'
```
Expected : `status: "escalated"` car client not found

## Points Clés à Vérifier

### Response de Première Étape
- [ ] `status` = `"awaiting_client_choice"`
- [ ] `available_slots` contient au minimum 2 créneaux
- [ ] Chaque créneau a : `slot_id`, `date`, `time`, `service_type`
- [ ] `session_id` est présent et unique
- [ ] `confidence` > 0.9

### Response de Confirmation
- [ ] `status` = `"resolved"`
- [ ] `appointment_details` contient :
  - `appointment_id`
  - `service_type`
  - `scheduled_date` (format ISO)
  - `status: "confirmed"`
- [ ] `confirmation_sent` contient email + phone
- [ ] `explanation` est claire et en français/anglais
- [ ] `confidence` = 0.95

## Logs Diagnostiques

Si quelque chose ne fonctionne pas, vérifier les logs :

```bash
# Dans le terminal où l'app est running, chercher les logs diagnostiques
# Prefix: 🔍 DIAGNOSTIC:

# Ou vérifier le fichier local (si disponible)
cat llm_diagnostics.log | grep -A 5 "PARSE_SUCCESS"
```

## Intégration Frontend

Pour intégrer dans une application frontend (web, mobile, IVR) :

### Étape 1 : Afficher la demande initiale
```javascript
// Appel initial
const response1 = await fetch('/agentic-cx', {
  method: 'POST',
  body: JSON.stringify({
    customer_id: customerId,
    message: userMessage
  })
});

const data1 = await response1.json();

if (data1.status === 'awaiting_client_choice') {
  // Afficher les créneaux au client
  displayAvailableSlots(data1.available_slots);
  storeSessionId(data1.session_id);
}
```

### Étape 2 : Client choisit et confirme
```javascript
// Quand le client clique sur un créneau
async function confirmSlot(slotId) {
  const response2 = await fetch('/agentic-cx/confirm-slot', {
    method: 'POST',
    body: JSON.stringify({
      customer_id: customerId,
      slot_id: slotId,
      session_id: storedSessionId
    })
  });

  const data2 = await response2.json();

  if (data2.status === 'resolved') {
    showConfirmationMessage(data2.appointment_details);
  }
}
```

## Questions Fréquentes

### Q: Pourquoi 2 endpoints et pas 1 seul ?
**R:** Pour clarté et flexibilité. Le premier endpoint ne booker rien (juste analyse et propose), le second endpoint finalise. Adapté pour chat, IVR, SMS qui ont des étapes distinctes.

### Q: Que se passe-t-il si le client choisit un créneau indisponible ?
**R:** Le système valide le `slot_id` avant de booker. Si le créneau n'existe plus → escalade avec message approprié.

### Q: Session ID a-t-il un timeout ?
**R:** Actuellement non (mocké en mémoire). En production, ajouter Redis avec TTL de 24h.

### Q: Peut-on toujours utiliser l'ancienne approche (auto-book) ?
**R:** Oui. Les anciens clients peuvent appeler `/confirm-slot` avec le premier créneau directement. Ou modifier le `_execute_rebooking` en l'initialisant avec `slot_id` du premier créneau.

## Documentation Complète

Pour plus de détails, voir :
- `FEATURE_SLOT_SELECTION.md` : Architecture technique complète
- `README.md` : Vue d'ensemble du projet
- `COMPREHENSIVE_DOCUMENTATION.md` : Architecture système globale

---

**Dernière mise à jour :** 16 janvier 2026
**Feature Status:** ✅ Testé et Prêt
