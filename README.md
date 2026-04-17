<h1 align="center">VisionLab — Visão Computacional</h1>

<p align="center">
  Processamento digital de imagens em tempo real com OpenCV e Flask
</p>

<p align="center">
  <img src="https://github.com/iuripedroso/VisionLab/blob/main/assets/tela%20principal.PNG?raw=true" width="700"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/OpenCV-4.8-5C3EE8?style=for-the-badge&logo=opencv">
  <img src="https://img.shields.io/badge/Flask-2.3-000000?style=for-the-badge&logo=flask">
  <img src="https://img.shields.io/badge/Visão-Computacional-ff3c6e?style=for-the-badge">
</p>

---

## ⌘ Sobre o Projeto

Este projeto é uma plataforma web interativa para **Processamento Digital de Imagens**, desenvolvida com Flask e OpenCV. Permite aplicar filtros, transformações morfológicas e rastreamento de objetos diretamente no navegador — sem instalar nada além do Python.

---

## ⌘ Funcionalidades

- 📷 Câmera interativa com efeitos em tempo real via streaming MJPEG
- 🖼 Processamento de imagens com visualização dos 8 bit planes
- 🎯 Rastreamento de objetos em vídeo com KCF Tracker + recuperação automática por template matching

---

## ⌘ Como Rodar

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/visionlab.git
cd visionlab/vision_app

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Inicie o servidor
python app.py

# 4. Acesse no navegador
# http://localhost:5000
```

---

## ⌘ Efeitos Disponíveis

| Efeito | Tipo | Descrição |
|--------|------|-----------|
| Cinza | Cor | Conversão para escala de cinza |
| Negativo | Cor | Inversão de cores `bitwise_not` |
| Binário | Cor | Limiarização automática Otsu |
| Canny | Cor | Detecção de bordas |
| Blur Média | Suavização | Média 5×5 |
| Blur Mediana | Suavização | Mediana 5 |
| Erosão | Morfologia | Reduz regiões claras |
| Dilatação | Morfologia | Expande regiões claras |
| Abertura | Morfologia | Erosão + Dilatação |
| Fechamento | Morfologia | Dilatação + Erosão |

---

## ⌘ Tecnologias Utilizadas

- Python
- Flask
- OpenCV
- NumPy

---

## ⌘ Observações

- A câmera usa o índice `0` por padrão (webcam principal)
- Vídeos enviados são salvos temporariamente em `uploads/` e sobrescritos a cada upload
- Para produção, substitua `debug=True` por um servidor WSGI como **Gunicorn**
