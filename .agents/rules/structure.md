# Projekt struktur 
Følgende projektstruktur skal overholdes:

- Alt test kode skal placeres i test folderen, og skal kunne afvikles med pytest.
- Alt projekt kode skal placeres under elpris package folderen.
- Alle dokumenter omkring koden, og projektet skal placeres i docs folderen, og være skrevet i markdown.
- Data til applikationen skal gemmes i data folderen. Eksempelvis database eller andre data filer. Der må gerne oprettes underfoldere til json, database eller tilsvarende hvis dette er nødvendigt for projektet. Data folderen oprettes når det er aktuelt hvis den ikke findes.
- Den eneste python fil der må være i roden af projektet er main.py. Denne forventes at kunne starte applikationen vha. uv run main.py
- Det tilstræbes at have en god struktur hvor kodefiler ikke bliver for store. Det er bedre at opdele strukturen i et mønster for models, ui (view) og control eksempelvis.
