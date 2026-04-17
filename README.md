# VisionLab 🎯

> Plataforma web interativa para Processamento Digital de Imagens com OpenCV e Flask.

---

## 📸 Preview

<!-- Substitua o caminho abaixo pela sua screenshot -->
![VisionLab Preview](docs/preview.png)

> _Adicione uma screenshot do app aqui. Basta colocar a imagem na pasta `docs/` com o nome `preview.png`, ou ajuste o caminho acima._

---

## ✨ Funcionalidades

- **Câmera Interativa** — aplique filtros em tempo real diretamente da webcam via streaming MJPEG
- **Processamento de Imagem** — carregue imagens, aplique transformações e visualize os 8 bit planes
- **Rastreamento de Objeto** — selecione um ROI em vídeo e acompanhe com KCF Tracker + recuperação por template matching

---

## 🗂 Estrutura do projeto

```
vision_app/
├── app.py                  # Backend Flask (rotas, streaming, processamento)
├── requirements.txt
├── templates/
│   ├── base.html           # Layout base com nav e sistema de toasts
│   ├── index.html          # Página inicial
│   ├── camera.html         # Módulo câmera interativa
│   ├── image.html          # Módulo processamento de imagem
│   └── tracking.html       # Módulo rastreamento de objeto
├── uploads/                # Vídeos enviados pelo usuário (gerado automaticamente)
└── docs/
    └── preview.png         # ← coloque sua screenshot aqui
```

---

## 🚀 Como rodar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/visionlab.git
cd visionlab/vision_app
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

> **Dependências:** `flask`, `opencv-python`, `numpy`

### 3. Inicie o servidor

```bash
python app.py
```

### 4. Acesse no navegador

```
http://localhost:5000
```

---

## 🎨 Módulos

### 📷 Câmera Interativa (`/camera`)

Abre o feed da webcam com streaming em tempo real. Efeitos disponíveis:

| Efeito | Descrição |
|--------|-----------|
| Cinza | Conversão para escala de cinza |
| Negativo | Inversão de cores (`bitwise_not`) |
| Binário | Limiarização automática (Otsu) |
| Blur Média | Suavização por média 5×5 |
| Blur Mediana | Suavização por mediana 5 |
| Canny | Detecção de bordas |
| Erosão | Operação morfológica de erosão |
| Dilatação | Operação morfológica de dilatação |
| Abertura | Morfologia: erosão + dilatação |
| Fechamento | Morfologia: dilatação + erosão |

---

### 🖼 Processamento de Imagem (`/image`)

Faça upload de uma imagem (JPG, PNG, BMP, TIFF) e:
- Aplique qualquer um dos 10 efeitos listados acima
- Visualize os **8 bit planes** individualmente (clique para usar como resultado)
- Baixe o resultado processado como PNG

---

### 🎯 Rastreamento de Objeto (`/tracking`)

1. Faça upload de um vídeo (MP4, AVI, MOV, MKV)
2. Clique em **Selecionar ROI** e arraste sobre o vídeo para marcar o objeto
3. O tracker KCF acompanha o objeto automaticamente
4. Em caso de perda, o sistema tenta recuperar via **template matching** (threshold 0.7)

---

## 🛠 Tecnologias

- **Backend:** Python 3, Flask
- **Visão Computacional:** OpenCV (`cv2`), NumPy
- **Frontend:** HTML5, CSS3 (vanilla), JavaScript
- **Streaming:** MJPEG via `multipart/x-mixed-replace`
- **Tracker:** KCF (via `cv2.legacy.TrackerKCF_create` ou `cv2.TrackerKCF_create`)

---

## ⚠️ Observações

- A câmera usa o índice `0` por padrão (webcam principal). Para trocar, altere `cv2.VideoCapture(0)` em `app.py`.
- Vídeos enviados são salvos temporariamente em `uploads/track_video.mp4` e sobrescritos a cada novo upload.
- O servidor deve ser executado em uma máquina com câmera conectada para o módulo de câmera funcionar.
- Para produção, substitua `app.run(debug=True)` por um servidor WSGI como **Gunicorn**.

---

## 📄 Licença

MIT — fique à vontade para usar, modificar e distribuir.
