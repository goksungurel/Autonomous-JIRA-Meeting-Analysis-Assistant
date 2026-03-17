# Örnek Toplantı Kararları ve JIRA Kuralları

## Geçmiş toplantı karar örnekleri

### Deployment & Release
- Production deploy kararları genelde bir sonraki sprintte uygulanır.
- Hotfix kararları 24 saat içinde uygulanır; DevOps ekibi bilgilendirilir.
- Bakım pencereleri önceden duyurulur; tipik pencere 02:00-06:00 arasıdır.
- Release öncesi QA onayı zorunludur.

### Performans & Teknik Borç
- Performans sorunları ilgili ekibe (Backend/Mobile) atanır.
- Mobil uygulama performans sorunları Mobile ekibine atanır.
- Teknik borç kararları bir sonraki sprintte planlanır.

### Dokümantasyon
- Dokümantasyon eksiklikleri ilgili ekip (Backend/Frontend/Mobile) tarafından 2 hafta içinde tamamlanır.
- API dokümantasyonu eksikse deadline 2 hafta olarak belirlenir.
- Model veya veri pipeline dokümantasyonu Data/AI ekibine atanır.

### Onboarding & İK
- Onboarding ve İK işleri İK ile koordinasyon gerektirir.
- Yeni stajyer/çalışan onboarding dokümanı İK ekibi tarafından hazırlanır.

### Data & AI
- Model performans sorunları Data/AI ekibine atanır.
- Veri pipeline hataları Data ekibine atanır, 1 hafta içinde çözülür.
- AI model güncellemeleri staging ortamında test edilir, sonra production'a alınır.

## JIRA görev formatı kuralları
- Başlık: Takım veya alan öneki kullan ([Backend], [Frontend], [Mobile], [Data], [AI], [DevOps], [İK]).
- Açıklama: Ne yapılacak, kim sorumlu, varsa tarih.
- Etiket önerileri: team-backend, team-frontend, team-mobile, team-data, team-ai, sprint-XX, documentation, performance, onboarding, hotfix, technical-debt, ml-model, data-pipeline.

## Priority kuralları
- Deadline açıkça belirtilmişse → Priority: High
- "Acil", "kritik", "bugün" ifadesi geçiyorsa → Priority: High
- Production veya müşteri etkisi varsa → Priority: High
- Bir sonraki sprint planlanmışsa → Priority: Medium
- "Araştır", "incele", "değerlendir" ifadesi geçiyorsa → Priority: Low
- Teknik borç veya iyileştirme ise → Priority: Low

## Karar → Görev örnekleri
- "Mobil uygulama yavaş" → [Mobile] Uygulama performans optimizasyonu | Priority: High | Etiket: team-mobile, performance
- "API v2 dokümantasyonu eksik, 2 hafta içinde tamamlanacak" → [Backend] API v2 dokümantasyonunu tamamla | Priority: High | Etiket: team-backend, documentation
- "Öneri modeli staging'de test edilecek" → [AI] Öneri modeli staging testini tamamla | Priority: Medium | Etiket: team-ai, ml-model
- "Veri pipeline'ında gecikme var, araştırılacak" → [Data] Veri pipeline gecikme sebebini araştır | Priority: Low | Etiket: team-data, data-pipeline