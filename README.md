# Vita+ — Site de saúde e bem-estar

Projeto escolar desenvolvido com Python, Flask, HTML, CSS, JavaScript e SQLite. O site roda localmente no navegador e não exige Streamlit, Pandas ou Visual Studio Build Tools.

## Requisitos
- Python 3.10 ou superior
- Navegador atualizado
- Internet apenas para instalar Flask; depois, as funções essenciais rodam localmente.

## Instalação no Windows
Abra a pasta `VitaPlus_Site` no Visual Studio Code. No menu Terminal > Novo Terminal, execute:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:5000` no navegador. Para parar o site, use `Ctrl+C` no terminal.

## Funcionalidades
- Painel inicial com resumo do dia.
- Perfil local editável.
- Registro de refeições e estimativa de calorias/macronutrientes por 100 g.
- Base local de alimentos comuns.
- Registro de peso e cálculo de IMC.
- Controle de água, atividades e hábitos.
- Planejamento de refeições por dia.
- Histórico e exportação CSV.

## Estrutura
- `app.py`: rotas e lógica web Flask.
- `database.py`: criação e consultas do SQLite e base alimentar.
- `templates/`: páginas HTML.
- `static/css/style.css`: estilos responsivos.
- `static/js/main.js`: interações de interface.

## Dados nutricionais e limites
Os valores por 100 g são aproximados e destinados à demonstração escolar; podem variar conforme marca e preparo. A base inicial não é uma importação oficial integral. Para uso real, consulte fontes reconhecidas como TACO/UNICAMP ou TBCA/USP e cite os dados utilizados. O IMC é apenas um indicador e não diagnostica doenças; para menores de 18 anos não se mostra classificação adulta. O sistema é local, de perfil único e sem autenticação; não publique dados pessoais. Não substitui orientação de profissionais de saúde.

## GitHub
```bash
git init
git add .
git commit -m "Projeto inicial Vita+"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
git push -u origin main
```
Substitua a URL de exemplo pela URL real. O banco `vita_plus.db` está no `.gitignore` e não deve ser publicado.
