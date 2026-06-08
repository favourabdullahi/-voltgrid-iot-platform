# ⚡ VoltGrid IoT Platform
### Real-Time Energy Grid Monitoring on Microsoft Azure

![Azure](https://img.shields.io/badge/Azure-Event%20Hubs-0078D4?logo=microsoftazure)
![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC?logo=terraform)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python)
![Status](https://img.shields.io/badge/Status-Live%20%26%20Verified-brightgreen)

---

## 📌 Overview

VoltGrid is a cloud-native, real-time IoT data pipeline that simulates smart energy devices transmitting telemetry to **Azure Event Hubs** every 2 seconds. The entire infrastructure is provisioned using **Terraform** (Infrastructure as Code), with no manual Azure Portal configuration required.

This project demonstrates:
- Event-driven architecture on Azure
- Infrastructure as Code with Terraform
- Python IoT device simulation
- Real-time data pipeline verification

---

## 🏗️ Architecture

```
IoT Simulator (Python)
        │
        │  JSON telemetry every 2s
        ▼
Azure Event Hub Namespace (litenergy-hub-ns)
        │
        ▼
Azure Event Hub (litenergy-events)
        │
        ▼
  [Ready for Stream Analytics / Azure Functions / Power BI]
```

---

## 🔧 Technologies Used

| Technology | Purpose |
|------------|---------|
| **Microsoft Azure** | Cloud platform |
| **Azure Event Hubs** | Real-time event ingestion |
| **Terraform** | Infrastructure as Code |
| **Python 3** | IoT device simulator |
| **azure-eventhub SDK** | Event publishing client |
| **Azure Cloud Shell** | Development environment |

---

## 📁 Project Structure

```
voltgrid-iot-platform/
├── README.md
├── terraform/
│   ├── main.tf            # Azure resources
│   ├── variables.tf       # Config variables
│   └── outputs.tf         # Connection string output
├── scripts/
│   └── simulator.py       # IoT device simulator
└── docs/
    └── architecture.md
```

---

## 🚀 Getting Started

### Prerequisites
- Azure account with active subscription
- Azure Cloud Shell (or local Azure CLI + Terraform)
- Python 3.8+

### Step 1 — Clone the Repository
```bash
git clone https://github.com/yourusername/voltgrid-iot-platform.git
cd voltgrid-iot-platform
```

### Step 2 — Deploy Azure Infrastructure
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Step 3 — Get Your Connection String
```bash
az eventhubs namespace authorization-rule keys list \
  --resource-group litenergy-dev-rg \
  --namespace-name litenergy-hub-ns \
  --name RootManageSharedAccessKey \
  --query primaryConnectionString \
  --output tsv
```

### Step 4 — Install Python Dependencies
```bash
pip install azure-eventhub
```

### Step 5 — Configure the Simulator
Open `scripts/simulator.py` and replace:
```python
CONNECTION_STR = "PASTE_YOUR_CONNECTION_STRING_HERE"
```
with your connection string from Step 3.

### Step 6 — Run the Simulator
```bash
python3 scripts/simulator.py
```

You should see:
```
✓ [smart_meter] device-001 (Lagos-North) — 87.45kW @ 225.3V [OK]
✓ [solar_panel] device-002 (Abuja) — gen=12.3kW [OK]
⚠️  [battery] device-003 (Kano) — charge=4.2% [CRITICAL_LOW]
```

---

## 📊 Verified Results

After running the simulator, Azure Portal confirmed:
- ✅ **Incoming Requests:** 169
- ✅ **Successful Requests:** 157
- ✅ **Incoming Messages:** 156

---

## 🔒 Security Note

**Never commit your real connection string to GitHub.**
The `CONNECTION_STR` value in `simulator.py` should always remain as a placeholder before pushing. Use Azure Key Vault or environment variables for production deployments.

---



---

## 👤 Author

**Favour Abdullahi**
Cloud & Infrastructure Engineer


---

## 📄 License

MIT License — free to use and modify with attribution.
