# ANARCHASTRA-161

**Yerel (Local-first) Multi-Ajan Çerçevesi**

![Status](https://img.shields.io/badge/Status-Active-success) ![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Runtime](https://img.shields.io/badge/Runtime-Ollama-white) ![License](https://img.shields.io/badge/License-MIT-blue)

Anarchastra-161, son kullanıcı donanımlarında yerel olarak çalışmak üzere inşa edilmiş otonom bir multi-ajan CLI (komut satırı) aracıdır. Donanımıma uygun olarak Ollama üzerinden açık kaynak modelleri kullanarak  API sınırlamalarını ve güvenlik filtrelerini atlayacak on-prem sistem hedeflenmektedir. 


```text
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣧⣶⣶⣶⣦⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣠⣾⢿⣿⣿⣿⣏⠉⠉⠛⠛⠿⣷⣕⠀⠀⠀⠀⠀⠀⢀⡀
⠀⠀⠀⠀⣠⣾⢝⠄⢀⣿⡿⠻⣿⣄⠀⠀⠀⠀⠈⢿⣧⡀⣀⣤⡾⠀⠀⠀
⠀⠀⠀⢰⣿⡡⠁⠀⠀⣿⡇⠀⠸⣿⣾⡆⠀⠀⣀⣤⣿⣿⠋⠁⠀⠀⠀⠀
⠀⠀⢀⣷⣿⠃⠀⠀⢸⣿⡇⠀⠀⠹⣿⣷⣴⡾⠟⠉⠸⣿⡇⠀⠀⠀⠀⠀
⠀⠀⢸⣿⠗⡀⠀⠀⢸⣿⠃⣠⣶⣿⠿⢿⣿⡀⠀⠀⢀⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠘⡿⡄⣇⠀⣀⣾⣿⡿⠟⠋⠁⠀⠈⢻⣷⣆⡄⢸⣿⡇⠀⠀⠀⠀⠀
⠀⠀⠀⢻⣷⣿⣿⠿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠻⣿⣷⣿⡟⠀⠀⠀⠀⠀⠀
⢀⣰⣾⣿⠿⣿⣿⣾⣿⠇⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣿⣅⠀⠀⠀⠀⠀⠀
⠀⠰⠊⠁⠀⠙⠪⣿⣿⣶⣤⣄⣀⣀⣀⣤⣶⣿⠟⠋⠙⢿⣷⡄⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣿⡟⠺⠭⠭⠿⠿⠿⠟⠋⠁⠀⠀⠀⠀⠙⠏⣦⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⡟⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
```

## Mimari

Sistem izole edilmiş (sandboxed) `workspace/` dizini içerisinde çalışır. Göreve bağlı olarak ilgili ajanlara dinamik model atamaları gerçekleştirir:

- **Coder Agent (`Qwen2.5-Coder-Abliterated`)**: Araç çağrılarını (tool-calls) yürütür, dosyaları modifiye eder ve kod yazar.
- **Reviewer Agent (`Qwen2.5-Coder-Abliterated`)**: Statik kod analizini (Ruff aracılığıyla) uygular ve yürütme mantığını doğrular. VRAM optimizasyonu için Coder modelini havuzdan (pool) yeniden kullanır.
- **Research Agent (`Hermes-3-Llama-3.1-8B`)**: Mantık ağaçlarında (logic trees) gezinir, eylem planları oluşturur ve karmaşık verileri yapılandırır.
- **Vision Agent (`Qwen3-VL:8B`)**: (Deneysel) Fiziksel dizilimleri ve görüntü girdilerini analiz eder.

## Ön Koşullar

- Python 3.10+
- Arka planda çalışan [Ollama](https://ollama.com/) servisi.



## Kurulum

Depoyu klonlayın ve ilgili dizinde `free` komutunu sistem genelinde kaydetmek için düzenlenebilir (editable) modda derleyin.

```bash
git clone https://github.com/4F71/Anarchastra-161.git
cd Anarchastra-161
pip install -e .
```

## Kullanım

İnteraktif REPL (Read-Eval-Print Loop) ortamını başlatmak için:

```bash
free
```


## Temel Prensipler

1. **Sıfır Harici İstek (Zero External Requests)**: Telemetri yok, API anahtarı yok, arka planda gizli ağ çağrıları yok.
2. **Deterministik Bağlam**: VRAM havuzları (pools) katı matematiksel ölçütlerle hesaplanır; ajanlar arası bağlam geçişleri 8GB sınırlarını aşmayacak şekilde tasarlanmıştır.
3. **Katı İzolasyon (Strict Sandboxing)**: Sistemin kök (root) çalışma alanı dışında rastgele kod yürütmesini engellemek için tüm I/O operasyonları `resolve_read_path` ve `resolve_write_path` fonksiyonlarıyla sınırlandırılmıştır.

---
*Lisans: MIT. 
