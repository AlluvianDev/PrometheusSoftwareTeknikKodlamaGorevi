🤖 Prometheus Autonomous Logistics Rover: Görev Koordinasyon Modülü

Bu proje, **Prometheus Autonomous Logistics Rover** için geliştirilen
**ROS 2 tabanlı Görev Koordinasyon Modülü** (Task Coordinator)
bileşenini içerir.

------------------------------------------------------------------------

📋 Proje Açıklaması

Bu modülün temel amacı, otonom rover'ın lojistik görevlerini merkezi bir
noktadan **yönetmek**, **sıralamak** ve **takip etmektir**.
Sistem, tamamen **asenkron ROS 2 mimarisi** üzerine kurulmuştur.

🔧 Temel Yetenekler

-   📷 **QR Kod İşleme**
    Kameradan (veya simülasyon kaynağından) gelen QR veri stringlerini
    ayrıştırır, *Task* nesnesine dönüştürür.

-   📊 **Öncelikli Kuyruk Yönetimi**
    Görevler öncelik değerine göre (1 en yüksek, 5 en düşük) sıralanır.

-   🤖 **Robot Navigasyon Entegrasyonu**
    Hedef koordinatlar Navigation modülüne gönderilir, görev sonucu
    dinlenir.

-   📡 **Durum Raporlama**
    Görev durumları (PENDING, IN_PROGRESS, COMPLETED) MQTT-benzeri bir
    topic üzerinden yayınlanır.

------------------------------------------------------------------------

## ⚙️ Kurulum ve Çalıştırma

Modül, **Ubuntu 24.04** ve **ROS 2 Jazzy Jalisco** üzerinde
geliştirilmiştir.

------------------------------------------------------------------------

📂 Yöntem 1: Manuel Kurulum (Standart)

ROS 2 kurulu bir sistem üzerinde kullanılır.

### 1. Çalışma Alanını Hazırlama

``` bash
mkdir -p ~/prometheus_ws/src
cd ~/prometheus_ws/src
```

Proje klasör yapısı şu şekilde olmalıdır:

    ~/prometheus_ws/src/task_coordinator/
     ├── package.xml
     ├── setup.py
     └── task_coordinator/
          ├── coordinator_node.py
          ├── navigation_mock_node.py
          ├── Task.py
          ├── TaskQueue.py
          └── QRParse.py

### 2. Derleme

``` bash
cd ~/prometheus_ws
colcon build --packages-select task_coordinator
```

✔️ Başarılı bir derlemede:

    Summary: 1 package finished

### 3. Ortam Kurulumu (Source)

Her yeni terminalde çalıştırılmalı:

``` bash
source ~/prometheus_ws/install/setup.bash
```

------------------------------------------------------------------------

## ▶️ Çalıştırma Adımları (Simülasyon)

Toplam **3 terminal** açılmalıdır.

------------------------------------------------------------------------

### **1. Terminal --- Koordinatör Node (Ana Beyin)**

``` bash
source /opt/ros/jazzy/setup.bash
source ~/prometheus_ws/install/setup.bash

ros2 run task_coordinator coordinator_node
```

------------------------------------------------------------------------

### **2. Terminal --- Navigasyon Simülasyonu**

``` bash
source /opt/ros/jazzy/setup.bash
source ~/prometheus_ws/install/setup.bash

ros2 run task_coordinator navigation_mock_node
```

------------------------------------------------------------------------

### **3. Terminal --- Test / QR Kod Gönderici**

``` bash
source /opt/ros/jazzy/setup.bash
source ~/prometheus_ws/install/setup.bash

ros2 topic pub --once /qr_code_data std_msgs/msg/String "data: 'ID:100;POS:5.0,2.0,0.0;PRIO:1;TYPE:delivery;TIMEOUT:90'"
```

------------------------------------------------------------------------

# 🐳 Yöntem 2: Docker ile Hızlı Kurulum

ROS 2 kurulu değilse önerilir.

### 1. Sistemi Başlatma

``` bash
docker compose up --build
```

### 2. Görev Gönderme

``` bash
docker exec -it qr_sender bash
```

İçeride:

``` bash
ros2 topic pub --once /qr_code_data std_msgs/msg/String "data: 'ID:50;POS:10.0,5.0,0.0;PRIO:1;TYPE:pickup;TIMEOUT:45'"
```

------------------------------------------------------------------------

# 🏗️ Kod Yapısı ve Tasarım

  --------------------------------------------------------------------------------
  Dosya                       Tür                 Açıklama
  --------------------------- ------------------- --------------------------------
  `coordinator_node.py`       ROS Node            Sistemin beynidir. ROS
                                                  mesajlarını yönetir.

  `navigation_mock_node.py`   ROS Node            Navigasyon biriminin taklididir.

  `TaskQueue.py`              Python Class        Görev sıralama ve yönetim
                                                  birimi.

  `QRParse.py`                Helper              QR string -\> Task dönüşümü.

  `Task.py`                   Model               Görev veri yapısı.
  --------------------------------------------------------------------------------

------------------------------------------------------------------------

# 📡 İletişim Akış Şeması

    A[Kamera / QR Kaynağı] -->|/qr_code_data| B(Coordinator Node);
    B -->|/navigation_goal| C(Navigation Mock Node);
    C -->|/navigation_result| B;
    B -->|/task_status| D[MQTT / Dashboard];

    subgraph "Logic Core"
    B -.-> E[TaskQueue Class]
    end

------------------------------------------------------------------------

## 👨‍💻 Geliştirici Notları

-   ✔️ **Öncelik Sistemi:** 1 = en acil\
-   ✔️ Hatalı QR formatları loglanır, sistem hata vermez\
-   ✔️ Modüler yapı ROS bağımlılıklarını düşük tutar

------------------------------------------------------------------------


