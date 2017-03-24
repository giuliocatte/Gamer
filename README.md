# Gamer (in attesa di un nome migliore)

Quando trovo la voglia scrivo anche questo file in inglese. Già buona parte delle docstring e dei commenti lo sono,
ma ho finito le energie al riguardo.

## Requirements

Il software è stato sviluppato con python 3.6, presumibilmente funziona anche con versioni precedenti, ma ho intenzione
di usare asyncio quindi sarà come minimo 3.4+

Come librerie esterne uso tensorflow (l'ho testato con l'installazione più stupida per mac senza gpu), numpy,
colorama per il forza4, e se non mi son perso qualcosa basta.

Si ringrazia https://github.com/DanielSlater/AlphaToe da cui ho copiato qualche fetta di codice, e anche imparato alcune
tecniche (qui: https://www.youtube.com/watch?v=Meb5hApAnj4).

## Usage

Per partire, è possibile eseguire il file test.py nella directory principale, verrà chiesto un po' di input circa la
configurazione della partita. Le reti neurali non funzioneranno se non vengono prima istruite, ad esempio per istruire la
rete neurale per il gioco del tris con i parametri standard, è sufficiente eseguire tictactoe/tf_training.py (sul mio mac
impiega circa 45 minuti).