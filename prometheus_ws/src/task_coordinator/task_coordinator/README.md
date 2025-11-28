🤖 Prometheus Autonomous Logistics Rover: Görev Koordinasyon Modülü (Task Coordinator)1. Proje AçıklamasıBu proje, Prometheus Autonomous Logistics Rover için geliştirilen Görev Koordinasyon Modülü'nü içermektedir5. Modülün temel sorumlulukları şunlardır:Lojistik görevleri yönetmek6.QR kodlarından gelen görevleri ayrıştırmak (Parse etmek)7.Navigasyon birimi ile entegre çalışmak8.Görev durumlarını MQTT (Mock) üzerinden raporlamak9.Proje, ROS 2 (Robot Operating System 2) Jazzy Jalisco ortamında Python dilinde geliştirilmiştir.2. Kurulum ve Çalıştırma TalimatlarıBu modülü çalıştırmak için Ubuntu 24.04 (Noble Numbat) ve ROS 2 Jazzy Jalisco ortamına ihtiyacınız vardır.A. Çalışma Alanını OluşturmaTerminalde aşağıdaki komutları çalıştırarak projenin çalışma alanını (Workspace) oluşturun ve derleyin:Bash# 1. Çalışma Alanı (Workspace) ve Kaynak klasörlerini oluştur
mkdir -p ~/prometheus_ws/src
cd ~/prometheus_ws/src

# 2. task_coordinator paketini kopyala/taşı (Sizin Github repo adınız olmalı)
# Örn: git clone [Sizin Repo Adresiniz]

# 3. Çalışma Alanına geri dön
cd ~/prometheus_ws

# 4. Paketi derle (build)
colcon build --packages-select task_coordinator

# 5. Ortamı kaynakla (Source the setup file)
source install/setup.bash
B. ÇalıştırmaProjenin tam simülasyonunu başlatmak için üç ana düğümü (Node) üç ayrı terminalde çalıştırmanız gerekir:Görev Koordinatörü (Task Coordinator Node): Kuyruk yönetimi ve durumu kontrol eder.Bashros2 run task_coordinator coordinator_node
Navigasyon Simülasyonu (Navigation Mock Node): Rover'ın hedefe hareketini simüle eder10.Bashros2 run task_coordinator navigation_mock_node
QR Kod Simülasyonu (Test Yayıncısı): Yeni bir görev stringini sisteme enjekte eder11.Bash# YENİ BİR GÖREV OLUŞTURULUYOR: ID:100, Öncelik: 1 (En Yüksek)
ros2 topic pub /qr_code_data std_msgs/msg/String "data: 'ID:100;POS:5.0,2.0,0.0;PRIO:1;TYPE:delivery;TIMEOUT:90'"

# İkinci bir görev ekleniyor: ID:101, Öncelik: 5 (En Düşük)
ros2 topic pub /qr_code_data std_msgs/msg/String "data: 'ID:101;POS:1.0,1.0,0.0;PRIO:5;TYPE:pickup;TIMEOUT:60'"
Not: Coordinator, önceliği 1 olan (ID:100) görevi önce çalıştıracaktır.3. Kod Yapısı ve Tasarım KararlarıBu modül, ROS 2'nin Node/Topic mimarisine uygun olarak, modülerlik ve asenkron çalışma temelinde tasarlanmıştır.A. Tasarım KararlarıModül/DosyaTürSorumluluklarPDF Gereksinimicoordinator_node.pyROS 2 Node (Düğüm)Ana Beyin. TaskQueue sınıfını yönetir, QR kodlarını dinler ve Navigasyona emir gönderir.Task Queue Yönetimi 12, MQTT Raporlama 13navigation_mock_node.pyROS 2 Node (Düğüm)Hedefleri alır, hareketi simüle eder ve sonucu Coordinator'a geri bildirir.Navigation Mock Sınıfı 14TaskQueue.pyPython Sınıfı (Veri Yöneticisi)Görevleri tutar, önceliğe göre sıralar ve durumları (PENDING, IN_PROGRESS, COMPLETED, FAILED, TIMEOUT) yönetir15. ROS iletişiminden bağımsızdır.Task Queue Yönetimi 16QRParse.pyPython FonksiyonuQR stringini ayrıştırır ve Task nesnesine dönüştürür. Hata yakalama içerir17.QR Koddan Görev Parse Etme 18B. İletişim AkışıGörevler, tamamen asenkron (eş zamanlı olmayan) ROS 2 Topics kullanılarak yönetilir:Giriş: Harici bir yayıncı (Test/Kamera) $\to$ /qr_code_data (Topic) $\to$ coordinator_node19.Yürütme: coordinator_node $\to$ /navigation_goal (Topic) $\to$ navigation_mock_node20.Geri Bildirim: navigation_mock_node $\to$ /navigation_result (Topic) $\to$ coordinator_node (Görevin tamamlandığını veya başarısız olduğunu bildirir)21.Raporlama: coordinator_node $\to$ /task_status (Topic) $\to$ MQTT/Dashboard (Görev durumunu yansıtır)22.