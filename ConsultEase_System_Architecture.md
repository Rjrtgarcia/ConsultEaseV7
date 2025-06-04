# ConsultEase System Architecture

## How to Use This Diagram

### Option 1: Mermaid Live Editor (Recommended)
1. Go to [Mermaid Live Editor](https://mermaid.live/)
2. Copy the simplified diagram code below
3. Paste it into the editor
4. View and export the diagram

### Option 2: GitHub/GitLab
- GitHub and GitLab automatically render Mermaid diagrams in markdown files
- Just commit this file and view it in your repository

### Option 3: VS Code Extension
- Install the "Mermaid Preview" extension
- Open this file and use the preview feature

### Option 4: Online Documentation
- Most documentation platforms (GitBook, Notion, etc.) support Mermaid

## Ultra-Simple Architecture (Compatible with Basic Mermaid)

```mermaid
graph TB
    A[Student] --> B[RFID Reader]
    B --> C[Raspberry Pi Central System]
    C --> D[PostgreSQL Database]
    C --> E[MQTT Broker]
    E --> F[ESP32 Unit 1]
    E --> G[ESP32 Unit 2]
    E --> H[ESP32 Unit 3]
    I[BLE Beacon 1] --> F
    J[BLE Beacon 2] --> G
    K[BLE Beacon 3] --> H
    F --> L[Faculty 1]
    G --> M[Faculty 2]
    H --> N[Faculty 3]
```

## System Flow (Step by Step)

```mermaid
graph TB
    Step1[Student scans RFID card]
    Step2[System authenticates student]
    Step3[Student selects faculty]
    Step4[System sends consultation request]
    Step5[Request appears on faculty desk unit]
    Step6[Faculty responds via buttons]
    Step7[Response sent back to student]
    
    Step1 --> Step2
    Step2 --> Step3
    Step3 --> Step4
    Step4 --> Step5
    Step5 --> Step6
    Step6 --> Step7
```

## Hardware Components

```mermaid
graph LR
    RaspberryPi[Raspberry Pi 4]
    ESP1[ESP32 Desk Unit 1]
    ESP2[ESP32 Desk Unit 2]
    ESP3[ESP32 Desk Unit 3]
    Beacon1[nRF51822 Beacon 1]
    Beacon2[nRF51822 Beacon 2]
    Beacon3[nRF51822 Beacon 3]
    
    RaspberryPi --> ESP1
    RaspberryPi --> ESP2
    RaspberryPi --> ESP3
    Beacon1 --> ESP1
    Beacon2 --> ESP2
    Beacon3 --> ESP3
```

## Communication Flow

```mermaid
graph TB
    Student --> CentralSystem
    CentralSystem --> MQTTBroker
    MQTTBroker --> ESP32Units
    BLEBeacons --> ESP32Units
    ESP32Units --> Faculty
    Faculty --> ESP32Units
    ESP32Units --> MQTTBroker
    MQTTBroker --> CentralSystem
    CentralSystem --> Student
```

## Simplified Compatible Diagram

```mermaid
graph TB
    %% Hardware Components
    subgraph Hardware["🔧 Hardware Components"]
        RPI["Raspberry Pi 4<br/>Touchscreen + RFID"]
        ESP1["ESP32 Unit 1<br/>TFT Display"]
        ESP2["ESP32 Unit 2<br/>TFT Display"]
        ESP3["ESP32 Unit 3<br/>TFT Display"]
        BEACON1["BLE Beacon 1"]
        BEACON2["BLE Beacon 2"] 
        BEACON3["BLE Beacon 3"]
    end

    %% Central System
    subgraph Central["🏠 Central System"]
        UI["Student/Admin UI"]
        Controllers["Controllers Layer"]
        Services["Services Layer"]
        Database["PostgreSQL DB"]
    end

    %% Communication
    subgraph Communication["📡 Communication"]
        MQTT["MQTT Broker"]
        BLE["BLE Protocol"]
        WiFi["WiFi Network"]
    end

    %% Connections
    RPI --> UI
    UI --> Controllers
    Controllers --> Services
    Services --> Database
    Services --> MQTT
    
    MQTT --> ESP1
    MQTT --> ESP2
    MQTT --> ESP3
    
    BEACON1 -.-> ESP1
    BEACON2 -.-> ESP2
    BEACON3 -.-> ESP3
    
    ESP1 --> WiFi
    ESP2 --> WiFi
    ESP3 --> WiFi
    WiFi --> MQTT
```

## Alternative: Network Topology Diagram

```mermaid
graph LR
    subgraph "Central System"
        A[Raspberry Pi 4]
        B[PostgreSQL DB]
        C[MQTT Broker]
        A --- B
        A --- C
    end
    
    subgraph "Faculty Desk Units"
        D[ESP32 Unit 1]
        E[ESP32 Unit 2]
        F[ESP32 Unit 3]
    end
    
    subgraph "BLE Beacons"
        G[nRF51822 #1]
        H[nRF51822 #2]
        I[nRF51822 #3]
    end
    
    C -.->|MQTT| D
    C -.->|MQTT| E
    C -.->|MQTT| F
    
    G -.->|BLE| D
    H -.->|BLE| E
    I -.->|BLE| F
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant S as Student
    participant R as RFID Reader
    participant UI as Central UI
    participant DB as Database
    participant MQTT as MQTT Broker
    participant ESP as ESP32 Unit
    participant B as BLE Beacon
    participant F as Faculty

    Note over S,F: Student Authentication Flow
    S->>R: Scan RFID Card
    R->>UI: Card ID
    UI->>DB: Verify Student
    DB-->>UI: Student Info

    Note over S,F: Consultation Request Flow
    S->>UI: Select Faculty & Send Request
    UI->>MQTT: Publish Request
    MQTT->>ESP: Forward Request
    ESP->>ESP: Display on TFT Screen

    Note over S,F: Faculty Presence Detection
    B->>ESP: BLE Advertisement
    ESP->>MQTT: Faculty Status Update
    MQTT->>UI: Update Faculty Status
    UI->>DB: Store Status

    Note over S,F: Faculty Response
    F->>ESP: Press Button (Accept/Busy)
    ESP->>MQTT: Response Message
    MQTT->>UI: Faculty Response
    UI->>S: Show Response
```

## Comprehensive System Architecture Diagram

```mermaid
graph TB
    %% Define styling classes
    classDef hardware fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef software fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    classDef database fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px,color:#000
    classDef protocol fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    classDef ui fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    classDef beacon fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000

    %% Hardware Layer
    subgraph HW ["🔧 Hardware Components"]
        RPI["📱 Raspberry Pi 4<br/>- 10.1&quot; Touchscreen (1024x600)<br/>- USB RFID Reader<br/>- WiFi/Ethernet<br/>- Central System Host"]
        
        subgraph DESK_UNITS ["ESP32 Faculty Desk Units"]
            ESP1["📺 ESP32 Unit #1<br/>- 2.4&quot; TFT Display (ST7789)<br/>- Blue/Red Response Buttons<br/>- WiFi Module<br/>- BLE Scanner"]
            ESP2["📺 ESP32 Unit #2<br/>- 2.4&quot; TFT Display (ST7789)<br/>- Blue/Red Response Buttons<br/>- WiFi Module<br/>- BLE Scanner"]
            ESP3["📺 ESP32 Unit #3<br/>- 2.4&quot; TFT Display (ST7789)<br/>- Blue/Red Response Buttons<br/>- WiFi Module<br/>- BLE Scanner"]
        end
        
        subgraph BLE_BEACONS ["nRF51822 BLE Beacons"]
            BEACON1["📡 Beacon #1<br/>MAC: AA:BB:CC:DD:EE:01<br/>Faculty Presence Detection"]
            BEACON2["📡 Beacon #2<br/>MAC: AA:BB:CC:DD:EE:02<br/>Faculty Presence Detection"]
            BEACON3["📡 Beacon #3<br/>MAC: AA:BB:CC:DD:EE:03<br/>Faculty Presence Detection"]
        end
        
        RFID["💳 RFID Cards<br/>Student Authentication"]
        TOUCH["👆 10.1&quot; Touchscreen<br/>Student Interface"]
    end

    %% Software Architecture - Central System
    subgraph CENTRAL ["🏠 Central System (Raspberry Pi)"]
        subgraph UI_LAYER ["📱 User Interface Layer"]
            STUDENT_UI["👥 Student Interface<br/>- PyQt5 Touchscreen UI<br/>- RFID Authentication<br/>- Faculty Selection<br/>- Consultation Requests"]
            ADMIN_UI["👨‍💼 Admin Dashboard<br/>- Faculty Management<br/>- System Monitoring<br/>- Consultation History<br/>- User Management"]
        end
        
        subgraph CONTROLLER_LAYER ["🎮 Controller Layer"]
            FACULTY_CTRL["Faculty Controller<br/>- Faculty Management<br/>- Presence Detection<br/>- Status Updates"]
            CONSULT_CTRL["Consultation Controller<br/>- Request Processing<br/>- Queue Management<br/>- Status Tracking"]
            ADMIN_CTRL["Admin Controller<br/>- User Management<br/>- System Configuration<br/>- Security Controls"]
            RFID_CTRL["RFID Controller<br/>- Card Authentication<br/>- Student Identification"]
        end
        
        subgraph SERVICE_LAYER ["⚙️ Service Layer"]
            MQTT_SERVICE["MQTT Service<br/>- Async Communication<br/>- Message Routing<br/>- Connection Management"]
            DB_SERVICE["Database Manager<br/>- Connection Pooling<br/>- Query Optimization<br/>- Transaction Management"]
            RFID_SERVICE["RFID Service<br/>- Card Reading<br/>- Hardware Interface"]
            HEALTH_SERVICE["System Health<br/>- Performance Monitoring<br/>- Error Tracking<br/>- Resource Management"]
        end
    end

    %% Database Layer
    subgraph DB_LAYER ["🗄️ Database Layer"]
        POSTGRES["🐘 PostgreSQL Database<br/>- Faculty Information<br/>- Student Records<br/>- Consultation History<br/>- Admin Accounts<br/>- System Logs"]
        
        subgraph MODELS ["📊 Data Models"]
            FACULTY_MODEL["Faculty Model<br/>- ID, Name, Department<br/>- BLE MAC Address<br/>- Status, Availability<br/>- Presence Detection"]
            STUDENT_MODEL["Student Model<br/>- ID, Name, Course<br/>- RFID Card ID"]
            CONSULT_MODEL["Consultation Model<br/>- Request Details<br/>- Status Tracking<br/>- Timestamps"]
            ADMIN_MODEL["Admin Model<br/>- Authentication<br/>- Permissions<br/>- Security Audit"]
        end
    end

    %% Communication Protocols
    subgraph PROTOCOLS ["📡 Communication Protocols"]
        MQTT_BROKER["🔄 MQTT Broker (Mosquitto)<br/>- Message Publishing<br/>- Topic Subscription<br/>- Quality of Service<br/>- Retained Messages"]
        
        BLE_PROTOCOL["📶 BLE Communication<br/>- Beacon Broadcasting<br/>- MAC Address Detection<br/>- RSSI Monitoring<br/>- Presence Validation"]
        
        WIFI_NETWORK["📶 WiFi Network<br/>- ESP32 Connectivity<br/>- MQTT Transport<br/>- System Integration"]
    end

    %% ESP32 Firmware Architecture
    subgraph ESP32_SOFTWARE ["📟 ESP32 Firmware"]
        DISPLAY_MANAGER["Display Manager<br/>- TFT Rendering<br/>- UI Layout<br/>- Message Display"]
        
        BLE_SCANNER["BLE Scanner<br/>- Beacon Detection<br/>- RSSI Filtering<br/>- Presence Logic"]
        
        MQTT_CLIENT["MQTT Client<br/>- Message Publishing<br/>- Status Updates<br/>- Command Reception"]
        
        BUTTON_HANDLER["Button Handler<br/>- Response Processing<br/>- User Input<br/>- State Management"]
        
        NETWORK_MANAGER["Network Manager<br/>- WiFi Connection<br/>- Reconnection Logic<br/>- Status Monitoring"]
    end

    %% Data Flow Connections
    
    %% Hardware to Software
    TOUCH --> STUDENT_UI
    RFID --> RFID_SERVICE
    ESP1 --> MQTT_BROKER
    ESP2 --> MQTT_BROKER
    ESP3 --> MQTT_BROKER
    
    %% BLE Connections
    BEACON1 -.->|BLE Advertising| ESP1
    BEACON2 -.->|BLE Advertising| ESP2
    BEACON3 -.->|BLE Advertising| ESP3
    
    %% Central System Internal Connections
    STUDENT_UI --> FACULTY_CTRL
    STUDENT_UI --> CONSULT_CTRL
    ADMIN_UI --> ADMIN_CTRL
    ADMIN_UI --> FACULTY_CTRL
    
    FACULTY_CTRL --> DB_SERVICE
    CONSULT_CTRL --> DB_SERVICE
    ADMIN_CTRL --> DB_SERVICE
    RFID_CTRL --> DB_SERVICE
    
    FACULTY_CTRL --> MQTT_SERVICE
    CONSULT_CTRL --> MQTT_SERVICE
    
    DB_SERVICE --> POSTGRES
    MQTT_SERVICE --> MQTT_BROKER
    RFID_SERVICE --> RFID_CTRL
    
    %% Database Model Connections
    POSTGRES --> FACULTY_MODEL
    POSTGRES --> STUDENT_MODEL
    POSTGRES --> CONSULT_MODEL
    POSTGRES --> ADMIN_MODEL
    
    %% ESP32 Internal Architecture
    ESP1 --> DISPLAY_MANAGER
    ESP1 --> BLE_SCANNER
    ESP1 --> MQTT_CLIENT
    ESP1 --> BUTTON_HANDLER
    ESP1 --> NETWORK_MANAGER
    
    %% MQTT Topics Flow
    MQTT_BROKER -->|consultease/faculty/1/messages| ESP1
    MQTT_BROKER -->|consultease/faculty/2/messages| ESP2
    MQTT_BROKER -->|consultease/faculty/3/messages| ESP3
    
    ESP1 -->|consultease/faculty/1/status| MQTT_BROKER
    ESP2 -->|consultease/faculty/2/status| MQTT_BROKER
    ESP3 -->|consultease/faculty/3/status| MQTT_BROKER
    
    ESP1 -->|consultease/faculty/1/responses| MQTT_BROKER
    ESP2 -->|consultease/faculty/2/responses| MQTT_BROKER
    ESP3 -->|consultease/faculty/3/responses| MQTT_BROKER

    %% Apply styling
    class RPI,ESP1,ESP2,ESP3,BEACON1,BEACON2,BEACON3,RFID,TOUCH hardware
    class STUDENT_UI,ADMIN_UI,DISPLAY_MANAGER ui
    class FACULTY_CTRL,CONSULT_CTRL,ADMIN_CTRL,RFID_CTRL software
    class MQTT_SERVICE,DB_SERVICE,RFID_SERVICE,HEALTH_SERVICE,BLE_SCANNER,MQTT_CLIENT,BUTTON_HANDLER,NETWORK_MANAGER software
    class POSTGRES,FACULTY_MODEL,STUDENT_MODEL,CONSULT_MODEL,ADMIN_MODEL database
    class MQTT_BROKER,BLE_PROTOCOL,WIFI_NETWORK protocol
    class BEACON1,BEACON2,BEACON3 beacon
```

## System Component Details

### 🔧 Hardware Components

**Central System (Raspberry Pi 4)**
- **Purpose**: Main system controller and user interface
- **Components**: 10.1" touchscreen, USB RFID reader, WiFi/Ethernet
- **Technologies**: Linux (Bookworm 64-bit), Python 3.9+, PyQt5

**ESP32 Faculty Desk Units**
- **Purpose**: Faculty-specific displays and presence detection
- **Components**: 2.4" TFT display (ST7789), response buttons, BLE scanner
- **Technologies**: Arduino C++, WiFi, MQTT client, BLE scanning

**nRF51822 BLE Beacons**
- **Purpose**: Faculty presence detection
- **Function**: Continuous BLE advertising with unique MAC addresses
- **Detection**: ESP32 units scan for specific beacon MAC addresses

### 📱 Software Architecture

**Frontend Layer (PyQt5)**
- Student interface for consultation requests
- Admin dashboard for system management
- Touch-optimized UI with on-screen keyboard support

**Backend Services**
- **MQTT Service**: Asynchronous communication with faculty desk units
- **Database Manager**: PostgreSQL connection pooling and query optimization
- **RFID Service**: Student authentication via RFID cards
- **System Health**: Performance monitoring and error tracking

**Database Layer (PostgreSQL)**
- Faculty information with BLE beacon mapping
- Student records and RFID authentication
- Consultation request tracking and history
- Admin accounts with security audit logging

### 📡 Communication Protocols

**MQTT (Message Queuing Telemetry Transport)**
- **Broker**: Mosquitto running on Raspberry Pi
- **Topics**: 
  - `consultease/faculty/{id}/messages` - Consultation requests to faculty
  - `consultease/faculty/{id}/status` - Faculty presence status
  - `consultease/faculty/{id}/responses` - Faculty responses (Accept/Busy)
- **QoS**: Level 1 for reliable message delivery

**BLE (Bluetooth Low Energy)**
- **Scanning**: ESP32 units continuously scan for faculty beacons
- **Detection**: MAC address-based presence validation
- **Thresholds**: RSSI filtering and debounce logic for stable detection

**WiFi Network**
- **Infrastructure**: Local network connecting all ESP32 units to central system
- **Security**: WPA2/WPA3 encryption for network security

### 🔄 Key Data Flows

1. **Student Authentication**: RFID card → RFID Service → Database lookup → UI authentication

2. **Consultation Request**: Student UI → Consultation Controller → MQTT Service → Faculty Desk Unit → TFT Display

3. **Faculty Presence Detection**: nRF51822 Beacon → ESP32 BLE Scanner → MQTT Status → Central System → Database Update

4. **Faculty Response**: Button Press → ESP32 → MQTT Response → Central System → Student Notification

5. **System Monitoring**: Health Service → Performance Metrics → Admin Dashboard → Real-time Alerts

### 🎯 Key Integrations

- **Admin Dashboard**: Complete system management with real-time monitoring
- **Faculty Management**: Automated presence detection with manual override options
- **Consultation Panel**: Queue management with priority handling
- **Audit Logging**: Complete security audit trail for compliance
- **Touch Interface**: Mobile-friendly UI with accessibility features

This architecture provides a robust, scalable solution for student-faculty consultation management with real-time presence detection and seamless communication across all system components.

## Research Defense - System Architecture Diagram

### Simplified Yet Comprehensive Architecture

```mermaid
graph TB
    %% Student Layer
    Student[👤 Student]
    RFID[💳 RFID Authentication]
    
    %% Central System
    CentralSystem[🖥️ Raspberry Pi 4 Central System<br/>PyQt5 Interface<br/>RFID Reader<br/>Database Manager]
    Database[(🗄️ PostgreSQL Database<br/>Faculty<br/>Students<br/>Consultations)]
    Admin[👨‍💼 Admin Dashboard<br/>System Monitor<br/>Faculty Management]
    
    %% Communication Hub
    MQTT[📡 MQTT Broker<br/>Real-time Messaging]
    WiFi[🌐 WiFi Network<br/>System Connectivity]
    
    %% Faculty Desk Units
    ESP32_A[📺 ESP32 Faculty Unit A<br/>TFT Display<br/>Accept/Busy Buttons]
    ESP32_B[📺 ESP32 Faculty Unit B<br/>TFT Display<br/>Accept/Busy Buttons]
    ESP32_C[📺 ESP32 Faculty Unit C<br/>TFT Display<br/>Accept/Busy Buttons]
    
    %% BLE Presence System
    Beacon_A[📶 BLE Beacon A<br/>Faculty Presence Detection]
    Beacon_B[📶 BLE Beacon B<br/>Faculty Presence Detection]
    Beacon_C[📶 BLE Beacon C<br/>Faculty Presence Detection]
    
    %% Faculty
    Faculty_A[👨‍🏫 Faculty A]
    Faculty_B[👨‍🏫 Faculty B]
    Faculty_C[👨‍🏫 Faculty C]
    
    %% Main Flow: Student Authentication
    Student --> RFID
    RFID --> CentralSystem
    
    %% Central System Operations
    CentralSystem --> Database
    CentralSystem --> Admin
    CentralSystem --> MQTT
    
    %% Communication Network
    MQTT --> WiFi
    WiFi --> ESP32_A
    WiFi --> ESP32_B
    WiFi --> ESP32_C
    
    %% Faculty Desk Units to Faculty
    ESP32_A --> Faculty_A
    ESP32_B --> Faculty_B
    ESP32_C --> Faculty_C
    
    %% BLE Presence Detection
    Beacon_A -.->|Presence Detection| ESP32_A
    Beacon_B -.->|Presence Detection| ESP32_B
    Beacon_C -.->|Presence Detection| ESP32_C
    
    %% Faculty Carries Beacons
    Faculty_A -.->|Carries| Beacon_A
    Faculty_B -.->|Carries| Beacon_B
    Faculty_C -.->|Carries| Beacon_C
    
    %% Response Flow Back
    Faculty_A --> ESP32_A
    Faculty_B --> ESP32_B
    Faculty_C --> ESP32_C
    
    ESP32_A --> MQTT
    ESP32_B --> MQTT
    ESP32_C --> MQTT
    
    %% Final Response to Student
    MQTT --> CentralSystem
    CentralSystem --> Student
```

## System Overview for Research Defense

### 🎯 **Core Functionality**
ConsultEase automates student-faculty consultation requests using IoT technology with real-time presence detection and instant communication.

### 🏗️ **System Architecture**

**Central Hub (Raspberry Pi 4)**
- Student interface with touchscreen and RFID authentication
- PostgreSQL database for all system data
- MQTT broker for real-time communication
- Admin dashboard for system management

**Faculty Desk Units (ESP32)**
- Individual display units for each faculty member
- TFT screen shows incoming consultation requests
- Physical buttons for Accept/Busy responses
- Built-in BLE scanner for presence detection

**Presence Detection System (nRF51822 BLE Beacons)**
- Each faculty member carries a unique BLE beacon
- ESP32 units continuously scan for faculty presence
- Automatic status updates when faculty arrive/leave

### 🔄 **System Workflow**

1. **Student Authentication**: RFID card scan for system access
2. **Faculty Selection**: Choose from available faculty on touchscreen
3. **Request Delivery**: MQTT sends consultation request to faculty desk unit
4. **Presence Verification**: ESP32 scans for faculty BLE beacon
5. **Faculty Response**: Physical button press (Accept/Busy)
6. **Instant Feedback**: Response sent back to student interface

### 💡 **Key Innovations**

**Automated Presence Detection**
- BLE beacons eliminate manual status updates
- Real-time faculty availability tracking
- Reduces student waiting time

**IoT Integration**
- MQTT protocol for reliable messaging
- WiFi-connected distributed system
- Scalable architecture for multiple faculty

**User-Friendly Interface**
- Touch-optimized design for accessibility
- RFID authentication for quick access
- Visual feedback for all interactions

### 📊 **Technical Stack**

**Hardware**: Raspberry Pi 4, ESP32, nRF51822 BLE Beacons, RFID Reader
**Software**: Python PyQt5, Arduino C++, PostgreSQL, Mosquitto MQTT
**Protocols**: MQTT, BLE, WiFi, RFID
**Features**: Real-time messaging, presence detection, touch interface

### 🏆 **System Benefits**

- **Efficiency**: Automated request handling and instant responses
- **Availability**: Real-time faculty presence tracking
- **Accessibility**: Touch-friendly interface with RFID authentication
- **Scalability**: Easy expansion for additional faculty members
- **Reliability**: Multiple communication protocols ensure system robustness 