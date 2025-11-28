🤖 Prometheus Autonomous Logistics Rover: Görev Koordinasyon Modülü
Bu proje, Prometheus Autonomous Logistics Rover için geliştirilen ROS 2 tabanlı Görev Koordinasyon Modülü'nü (Task Coordinator) içerir.
📋 Proje AçıklamasıBu modülün temel amacı, otonom rover'ın lojistik görevlerini merkezi bir noktadan yönetmek, sıralamak ve takip etmektir. Sistem, asenkron ROS 2 mimarisi üzerine kurulmuştur.Temel Yetenekler:📷 QR Kod İşleme: Kameradan (simüle edilen) gelen QR kod verilerini ayrıştırarak görev nesnelerine dönüştürür.📊 Öncelikli Kuyruk Yönetimi: Görevleri öncelik değerine (1-5 arası, 1 en yüksek) göre otomatik sıralar.robot Navigasyon Entegrasyonu: Hedef koordinatları navigasyon birimine iletir ve varış durumunu takip eder.📡 Durum Raporlama: Görevlerin anlık durumunu (PENDING, IN_PROGRESS, COMPLETED) MQTT benzeri bir yapı ile raporlar.⚙️ Kurulum ve ÇalıştırmaBu proje Ubuntu 24.04 işletim sistemi ve ROS 2 Jazzy Jalisco sürümü üzerinde geliştirilmiştir.📂 Yöntem 1: Manuel Kurulum (Standart)Eğer sisteminizde ROS 2 yüklü ise bu yöntemi kullanın.1. Çalışma Alanını HazırlamaTerminale aşağıdaki komutları sırasıyla yapıştırın:Bash# Klasör yapısını oluştur
mkdir -p ~/prometheus_ws/src
cd ~/prometheus_ws/src

# NOT: Proje dosyalarını buraya kopyalayın.
# Doğru dosya ağacı şu şekilde görünmelidir:
# ~/prometheus_ws/src/task_coordinator/
#    ├── package.xml
#    ├── setup.py
#    └── task_coordinator/
#         ├── coordinator_node.py
#         ├── navigation_mock_node.py
#         ├── Task.py
#         ├── TaskQueue.py
#         └── QRParse.py
2. Derleme (Build)Kodları sisteme tanıtmak için derleme işlemi yapılmalıdır.Bashcd ~/prometheus_ws
   colcon build --packages-select task_coordinator
   ✅ Başarılı bir derleme sonucunda Summary: 1 package finished yazısını görmelisiniz.3. Ortam Kurulumu (Source)Her yeni terminal açtığınızda, ROS 2'nin paketimizi tanıması için şu komutu girmelisiniz:Bashsource ~/prometheus_ws/install/setup.bash
   ▶️ Çalıştırma Adımları (Simülasyon)Sistemi tam olarak test etmek için 3 farklı terminal açmanız gerekmektedir.1. Terminal: Görev Koordinatörü (Ana Beyin) 🧠Bu düğüm, gelen görevleri sıraya alır ve yönetir.Bashsource /opt/ros/jazzy/setup.bash
   source ~/prometheus_ws/install/setup.bash

ros2 run task_coordinator coordinator_node
2. Terminal: Navigasyon Simülasyonu 🚀Bu düğüm, robotun hareketini simüle eder (3 saniye bekler ve "Tamamlandı" der).Bashsource /opt/ros/jazzy/setup.bash
   source ~/prometheus_ws/install/setup.bash

ros2 run task_coordinator navigation_mock_node
3. Terminal: Test / QR Kod Gönderici 📲Bu terminalden sanki bir kamera QR kod okumuş gibi sisteme görev gönderilir.Bashsource /opt/ros/jazzy/setup.bash
   source ~/prometheus_ws/install/setup.bash

# Örnek bir görev gönder (ID:100, Öncelik:1 - En Yüksek)
ros2 topic pub --once /qr_code_data std_msgs/msg/String "data: 'ID:100;POS:5.0,2.0,0.0;PRIO:1;TYPE:delivery;TIMEOUT:90'"
🐳 Yöntem 2: Docker ile Hızlı Kurulum (Bonus)Bilgisayarınızda ROS 2 kurulu değilse veya kurulumla uğraşmak istemiyorsanız Docker kullanabilirsiniz.Gereksinimler: Docker Desktop veya Docker Engine.1. Sistemi Başlatma:Projenin ana dizininde (Dockerfile'ın olduğu yer) şu komutu çalıştırın:Bashdocker compose up --build
Bu komut tüm sistemi otomatik kurar ve başlatır.2. Görev Gönderme (Test):Sistem çalışırken yeni bir terminal açın ve test konteynerine bağlanın:Bashdocker exec -it qr_sender bash
İçeri girdikten sonra görev gönderme komutunu kullanabilirsiniz:Bashros2 topic pub --once /qr_code_data std_msgs/msg/String "data: 'ID:50;POS:10.0,5.0,0.0;PRIO:1;TYPE:pickup;TIMEOUT:45'"
🏗️ Kod Yapısı ve Tasarım KararlarıProje, ROS 2'nin dağıtık ve asenkron yapısına uygun olarak Modüler bir şekilde tasarlanmıştır.Dosya AçıklamalarıDosyaTürGörevicoordinator_node.pyROS NodeSistemin beyni. ROS iletişimini yönetir ancak mantığı TaskQueue sınıfına devreder.navigation_mock_node.pyROS NodeNavigasyon birimini simüle eder. Hedefe gitme süresini time.sleep ile taklit eder.TaskQueue.pyPython ClassData Manager. Görevleri hafızada tutar, önceliğe göre sıralar ve durumlarını yönetir. ROS'tan bağımsızdır.QRParse.pyHelperGelen ham string verisini (ID:42...) işleyip Task nesnesine çeviren yardımcı sınıftır.Task.pyModelGörev veri yapısını tanımlar (ID, Pozisyon, Öncelik vb.).📡 İletişim Akış ŞemasıSistem, düğümler arasında Topic (Yayınla/Abone Ol) yapısını kullanır:Kod snippet'igraph TD;
A[Kamera / QR Kaynağı] -->|/qr_code_data| B(Coordinator Node);
B -->|/navigation_goal| C(Navigation Mock Node);
C -->|/navigation_result| B;
B -->|/task_status| D[MQTT / Dashboard];

    subgraph "Logic Core"
    B -.-> E[TaskQueue Class]
    end
Giriş: qr_code_data üzerinden gelen veri QRParse ile işlenir ve TaskQueue'ya eklenir.İşlem: Coordinator Node, sıradaki görevi navigation_goal üzerinden gönderir.Sonuç: Navigation Mock, görevi tamamlayınca navigation_result döner.Rapor: Her aşama task_status üzerinden raporlanır.👨‍💻 Geliştirici NotlarıÖncelik Mantığı: Düşük sayı = Yüksek Öncelik (1 en acil, 5 en düşük).Hata Yönetimi: Hatalı QR formatları veya bilinmeyen görev tipleri sistem tarafından yakalanır ve loglanır (Sistemi çökertmez).
