# co to za projekt?
Discordowy bot, który ma co jakiś czas sprawdzać wybrane strony internetowe (zazwyczaj fora) i jeśli pojawi się na nich nowa treść (posty), wysyłać ją w wiadomości na wybranym kanale na discordowym serwerze. Powinno dać się dodawać nowe strony z poziomu komend na discordzie, a także zmieniać komendami ustawienia. Kod, który odpowiada za przeglądanie stron, powinien być dodawany jako pluginy.

# MVP:
- przeglądanie stron internetowych i podsyłanie wiadomości
- dodawanie nowych stron, ustawień
- pluginy (pierwszy plugin na pewno)

# Nice to have:
- grupowanie postów w tagi
- wzmianki
- możliwość odpowiadania na wiadomości
- filtry
- pluginy pod tematy forum

# Kiedy projekt będzie ukończony?
- wersja 0: MVP - program musi po prostu działać
- wersja 1: osobna konfiguracja dla każdego serwera
- wersja 2: pluginy do tematów, wzmianki, filtry, odpowiadanie na wiadomości (to nie znaczy, że mam zrobić jakieś komendy), tagi

# co to plugin?
Klasa, która będzie miała metodę `__await__` albo `get_messages()`, która odpowiada za generowanie wiadomości ze strony. Po drodze musi wysyłać żądania http do strony tak długo, dopóki będzie od niej dostawać nie przeczytane posty. Każdą stronę parsuje, by pozyskać link następnej strony, a także treść każdego posta.

# na później:
- ~~Użycie markdownify niekoniecznie jest czymś, na co każdy by wpadł, zwłaszcza w takiej formie, jak robię to ja. Przeniósłbym swoją funkcję do klasy Message~~ DONE
- Osobna konfiguracja dla każdego serwera

# TODO:
- napisać ładne todo
- udokumentować obecny stan projektu (zaczynam pisać go bardzo chaotycznie)

# plan crawlera

zakładam, że dostanę link do konkretnej kategorii forum (np. ogłoszenia na anglojęzycznej części, dyskusja o mechanice na polskojęzycznej)

0. Crawler będzie miał osobny task działający co ileś minut (da się to zrobić w discord api - <https://discordpy.readthedocs.io/en/stable/ext/tasks/index.html>).
Robię w nim rutyny dla każdego tematu - najpierw wyślij żądanie o temat, potem parsuj i wysyłaj kolejne żądania o kolejne strony, jeśli trzeba.
1. Przejdź po wszystkich tematach, trzymaj listę dat aktualizacji. Szukaj wszystkich tematów ze zbioru tematów, które mnie interesują. Jeśli dojdę do tematu, który nie został od dawna zaktualizowany, to przestaję sprawdzać dalej. Chciałbym przeglądać na podstawie daty podanej w tym pliku, ale zamiast tego wywołam rutynę dla tego tematu. Jeśli funkcja zauważy, że temat od dawna się nie zmienił, to szybko zwróci info.
2. Sprawdź listę postów. Chciałbym, żeby patrzyć na ich liczbę albo datę aktualizacji, ale to problematyczne - posty mogą zostać skasowane. Data aktualizacji nie daje mi odpowiednich info, ale mogę ją porównywać, by ewentualnie darować sobie dalsze sprawdzanie (nie wiem co z edycjami). Idź w górę od ostatniego posta tak długo, dopóki napotykasz nowe id postów.
3. Jeśli przejdziesz całą stronę, udaj się na poprzednią (jeśli jest).
4. Iterując po tematach, zrób instrukcję await asyncio.sleep(), po czym wywołaj rutynę z requestem do niego.
5. Jeśli pojawi się nowy temat na liście, daj prompt

## Potrzebuję się przyjrzeć tematom

1. strona z tematami:
    ** źle to parsowałem, wszystko znajduje się w:**
    ```html
    <tr itemscope itemtype="http://schema.org/Article" class='__topic  expandable' id='trow_784081' data-tid="784081">
    ```
    I tutaj też znajdzie się data ostatniego postu - a następnie id, jeśli tam pójdę. To jest tak, próbuję zrobić to wydajnie. Powiedzmy, że w tym momencie id mnie nie obchodzi. Nie optymalizuję na siłę. Tylko, że stron z tematami jest z ponad 100. Nie chcę wysyłać tyle żądań. Wolę wysyłać żądania do momentu, kiedy znajdę ostatni post lub pójdę za daleko (pozostałe posty są za stare). Ale chyba jednak wystarczy mi to:
    ```html
    <a itemprop="url" id="tid-link-784081" href="http://forum.worldoftanks.eu/index.php?/topic/784081-the-supertest-is-coming-to-the-eu/" title='The Supertest is coming to the EU&#33; View topic, started  10 May 2022 - 01:17 PM' class='topic_title' >
    ```

    Bo to się ładnie wyskaluje. Nie wszystkie tematy są intensywnie przeglądane, zazwyczaj.

   
2. strona z postami:

    ```html
    <div class='post_block__colored post_block hentry clear clearfix ' id='post_id_18962125'>
    ```
    
    - klasa - pozwoli stwierdzić, że to post
    - id - identyfikator posta (pisałem - chcę iść dopóki nie znajdę znany mi post)

    ```html
    <div itemscope itemtype="http://schema.org/UserComments" class='post_wrap' >
    ```

    - ten div znajduje się w post_block
    - klasa mi go pozwoli zmapować

    ```html
    <h3 class='row2'>
            <span itemprop="creator name" class="author vcard b-author b-author">Nishi_Kinuyo
                <span class='b-author_shadow'></span>
            </span>
        
        
        <span class='post_id right ipsType_small desc blend_links'>
            
                <a itemprop="replyToUrl" href='http://forum.worldoftanks.eu/index.php?/topic/784081-the-supertest-is-coming-to-the-eu/page__pid__18962125#entry18962125' rel='bookmark' title='The Supertest is coming to the EU&#33;Link to post #2'>
            
            #2
            </a>
        </span>
        
        <span class='posted_info b-posted_info desc lighter ipsType_small'>
            Posted <abbr class="published" itemprop="commentTime" title="2022-05-11T15:41:01+00:00">11 May 2022 - 04:41 PM</abbr>
        </span>
    </h3>
    ```

    - to znajduje się w post_wrap
    - span z "creator name" zawiera nick autora
    - span z klasą "posted_info" zawiera datę stworzenia posta (może mi się nie przydać)

    ```html
    <div class='author_info'>
    ```
    - znajduje się w post_wrap

    ```html
    <div class='user_details'>
    ```

    - znajduje się w author_info

    ```html
    <ul class='basic_info'>
    ```
    
    - znajduje się w user_details
    - zawiera info o użytkowniku - mnie interesuje tylko tytuł, który jest w `<li class='group_title'>`

    ```html
    <div class='post_body'>
    ```

    - no i to mięsko znajduje się w post_wrap
    - mięsko. treść posta. nie zamierzam jej parsować. Po prostu ją wyświetlę. Ewentualnie napiszę coś, co te world-of-tanksowe spoilery zamieni w blok tekstu. Pojawia się moje pytanie, jak obsłużę za długie posty. Ale to potem. Mogę dać wstęp i resztę w pliku. Nie mam sił tego analizować. Są tam komentarze, spoilery, potencjalnie grafiki i filmiki.
    - jeśli chodzi o spoilery, mogę użyć get_text() - zignoruje wszystkie tagi i wklei mi sam tekst po środu (mięsko) - jedyne co pozostaje, to wykryć tag oznaczający spoilery i zamienić go na blok tekstu w md. Interesuje mnie bbc_spoiler_wrapper
        ```html
        <input type="button" class="bbc_spoiler_show" value="Show "><div class="bbc_spoiler_wrapper">
        ```
        myślę escapować div, input i span z wiadomości
    

Chciałem, by mieć pluginy - parsery. Albo crawlery. Właśnie w tym problem. Nie zdecydowałem, jak to ma działać, co ma być tym pluginem. Są dwie opcje.
1. Wiele producerów, jeden consumer
2. Wiele producerów, każdy ma consumera

Jednym z problemów jest to, że producer nie zwraca od razu po pierwszym żądaniu wyniku - może się wywoływać rekurencyjnie. Chcę zachować kolejność postów podczas wysyłania wiadomości, zwłaszcza - chcę zachować ciągłość. To znaczy, żeby wysłało mi jednym ciągiem wszystkie posty z jednego forum, z jednego tematu. Kolejność for jest dowolna. Kolejność tematów też. Kolejność postów musi być zachowana. Od ostatniego czasu mogło się pojawić wiele stron w temacie. Każda strona wymaga osobnego requesta, bo szukam najnowszego postu. A nie chcę robić tych requestów za dużo. Ale w sumie... Producer nie musi być rekurencyjny. Może wywołać na początku x żądań - tyle, ile potrzebuje. Tyle tylko, że to kosztuje pamięć.

Pierwsza opcja: wywołuj producera aż do momentu, kiedy przetworzy wszystkie posty. Dopiero wtedy przekaż posty dalej. W tym samym momencie nie muszę przechowywać wszystkich plików html. Dla tematu z ponad 100 stronami, to jest bezpieczniejsze.

Teraz jak tak myślę, to ulegam "premature optimisation is a root of all evil". Nie ma co silić się na optymalizację. Ważniejsza jest organizacja. Zacznę od funkcji rekurencyjnej. Powiedzmy, że daje ona jakiś wynik. Musi go w końcu dać. A to, czy wyśle x żądań i je zbierze, czy będzie obsługiwać po jednym, to już implementacja. Znaczy, nie funkcja rekurencyjna, a klasa - producer. Dobra. Co dalej. Producer - w jakiś sposób, nie obchodzi mnie jaki - daje wynik. Gdy da wynik, powinien się usunąć. Przynajmniej jeśli to post_producer. Bo teraz kwestia, że będzie też producer tematów. I producer forum. Uh.

Jeśli mam forum, to mam też listę tematów. Teraz tak. Każdy temat ma linki. ForumProducer może skorzystać ze znanej sobie listy tematów - przeszukać się rekurencyjnie w poszukiwaniu linków. Z drugiej strony, może nie chcę uzależniać się od forów. Może mój scraper będzie też przeglądał jakieś strony z newsami - choć te chyba wolą, z powodu licencji, tego uniknąć. No ale dobra. Poza tym uwzględniam możliwość połączenia tego bota z RSS. Na pewno chciałbym mieć funkcję "przeszukaj forum w poszukiwaniu linków", ale chciałbym też grupować

No to na start wolałbym coś takiego: mam nie forum, a grupę tagów. Każdy link może mieć jeden tag, dodawany podczas zapisywania linku. Tyle. I teraz nie przeszukuję forum w poszukiwaniu tematów. Temat mam jeden. **sygnalizowałbym koniec tematu, swoją drogą**. I zamiast ForumProducera mam TagProducera. Normalnie zająłbym się jednym tagiem. Ale jest to mało wydajne. Lepsze byłoby mieć konsumera do tagów - który by wysyłał wiadomości gotowego tagu, gdy jest to tylko możliwe. Wysyłanie wiadomości jest powolne, więc nawet tym bardziej wolę, by to robione było na bieżąco. Teraz tak. TagConsumer jest jeden i może zajmować się w tym samym momencie jednym tagiem. Nie może wysyłać wielu na raz. Zresztą, nie wiem, czy aby bot byłby "TagConsumerem". Bo to on zawiera metodę client.send. Więc mogę pracować na innych tagach, ale ostatecznie oddać mogę tylko jeden do pracy. Tzn. mogę jeszcze załadować drugi tag. Dobra.

TagConsumer robi to: zapisuje posty do historii, aktualizuje ją, przygotowuje post zbiorczy oraz posty pojedyncze. Myślę, że chcę zapisywać posty pojedyncze do pliku i jedynie je wyciągać, gdy trzeba.



Muszę sobie to wyobrazić inaczej. Nie mogę wysyłać jednego 

*na marginesie: tu widzę, że przyda się też, by botem dało się zarządzać przez komendy - oooooof*
*sygnalizować koniec tematu userowi*
*zdecydować czy chcę podesłać cały post czy tylko link, jeśli jest za długi, no i jego streszczenie. To wpłynie na pracę producera - może wysłać jedną wiadomość na tag, a może kilkadziesiąt*. Wysłałbym ewentualnie jedną, zbiorczą, no i dał możliwość poproszenia o treść wiadomości. I możliwość domyślnego proszenia.


Za dużo feature ciągle mi przychodzi do głowy. Muszę to ładnie streścić.

Bot woła TagProducerów. Oni mają linki do śledzonych stron i info o parserach używanych na tych stronach. Jest też TagConsumer. On przejmuje od TagProducerów przerobione tagi. Do kolejki. Każdy tag przetwarza. Tzn. kiedy tag już jest gotowy, to trzeba będzie pozapisywać do plików pewne dane, pewne też trzeba będzie podesłać na discorda. W tym samym czasie obsługuje tylko jeden tag, ale jako, że wysyłanie wiadomości kosztuje czas, to go oddaje programowi. Wiadomości są wysyłane jedna po drugiej, co trochę zajmuje.

TagProducerzy wywołują PageProducerów. Oni odpowiadają za żądania do każdej ze stron na danym tagu. PageProducer zna tylko jeden parser - ten potrzebny do swojej pracy. Musi zescrapować całą swoją stronę. Tu się zastanawiam nad jednym, co to jest ta strona. Tag jest sztuczny, stworzony przez użytkownika. Strona to np. konkretny temat na forum. Czyli nie muszę przeglądać listy tematów. Teraz mnie zastanawia, co ja chciałem wcześniej osiągnąć. Chyba podczas projektowania myślałem o aktualizowaniu listy wszystkich tematów - co jest słuszne, bo mamy sobie to nasze forum nerthusa. I tu się pojawia drobna rekurencja. Jeśli zadam botowi śledzić konkretne tematy na forum nertha, to będzie śledził tylko je. Jak mu zadam śledzić całe forum nertha, to będzie sprawdzał najnowsze tematy i podsyłał z nich wiadomości. Dobra. Widzę. Bo wcześniej myślałem o przeszukiwaniu listy tematów w sumie. A potem wymyśliłem tag. Albo tag wymyśliłem dopiero, gdy zacząłem myśleć o przeszukiwaniu wszystkich działów forum. Tak. Pewnie to. Bo wciąż chcę śledzić zmiany też w danym dziale. ... Muszę przemyślić od zera.

Ważne jest to, że nie chcę na siłę tego optymalizować przed zaprojektowaniem, ale też chcę dobrze wykorzystać async - muszę więc mądrze zaprojektować aplikację, by była wydajna.

-----------------------------

Bot ma dwie osobne części. Pierwsza to klient. Druga to pluginy. Plugin to klasa, której obiekty po wywołaniu mają zwrócić listę przygotowanych do wysłania wiadomości. **Która część aplikacji powinna przygotowywać wiadomości do wysłania? Co, jeśli będę chciał zinterpretować spoilery na forum jako spoilery na discordzie? Albo, jeśli będę chciał wysłać podesłany na forum kod w postaci bloku z podświetlaną składnią? Pierwsza opcja, to żeby każdy plugin sam interpretował wiadomości. Druga, że bot będzie je interpretował jako czysty tekst i resztę doda sam (np. wzmianki). Chciałbym, żeby to bot odpowiadał za rozbijanie wiadomości. Przemawia za tym myśl, żeby twórca pluginu się tym nie przejmował. Problem jest wtedy, kiedy będzie chciał w jakiś konkretny sposób wysłać wiadomość - może będzie przekazywał flagi botowi? MNIEJSZA, ZANOTUJĘ SOBIE TO.**
Plugin może przyjmować jako argumenty jakiś json z konfiguracją.

*Czy chcę użyć wielu wątków dla każdego serwera? Na razie nieważne.*

Klient zajmuje się wczytywaniem i zapisywaniem konfiguracji. Obsługuje wiadomości - każdy task od usera dostaje plugin, który wybiera ten user. **tu trzeba zapamiętać "piekło to użytkownik" i wyłapać wyjątki**. Bot co wyznaczoną ilość czasu wysyła żądanie do wybranego pluginu (wykonuje taska), a ten zwraca mu po jakimś czasie listę wiadomości. Bot je wysyła. **Konfiguracja pluginu jest bardzo ważna: może dostać np. headery do żądań http. Poza tym, nie wiem na ile to zawiera się w konfiguracji taska - chyba nie. Albo i zależy. Bo plugin forum wota nie potrzebuje ładować headerów z zewnątrz, bo ma swoje. Ale mogę stworzyć ogólniejszy plugin i chcieć mu wysyłać te headery. Mogę chcieć dodawać do taska wzmianki albo okres, w którym mam ten task wykonywać. No i mogę napisać, na jakim kanale to ma być. I czy ma być spakowane do spoilera. Obecne pluginy, jakie mam w głowie, nie muszą korzystać z komend discorda, ale nie wykluczam takiej opcji. Wtedy będę musiał przekazywać pluginowi dane z kanału/serwera. Albo, pluginy będą mogły wykonywać metody z clientem w argumencie.**

Muszę poczytać, do czego służą sesje http. Bo one mi utrudniają sprawę. Tak czy inaczej, sesję trzeba wywołać w obrębie pluginu, bo bot może zlecać zadania pluginom nie mającym nic wspólnego z http. Problem jeszcze polegał na tym, że w sumie to nie mogę wywoływać await przy otwartej sesji, bo z niej wyjdę.

W skrócie, sesja jest najbardziej optymalna, bo nie musisz robić połączenia za każdym razem - bo przecież i tak wybrałeś już async.

Tak naprawdę, nie wiem co robić.
- czy sesja musi być otwarta dla każdego serwera dc z osobna? czy może jedna dla całej aplikacji? Czym to się różni?
- jeśli sesja będzie otwarta dla całej aplikacji, to czy ma jakieś limity? W sensie, co jeśli będę chciał wysyłać równolegle żądania dla każdego z serwerów? Czy użycie jednej sesji będzie mnie spowalniać?

```
Session encapsulates a connection pool (connector instance) and supports keepalives by default. Unless you are connecting to a large, unknown number of different servers over the lifetime of your application, it is suggested you use a single session for the lifetime of your application to benefit from connection pooling.
```

W moim konkretnym przypadku będę miał właśnie wiele różnych serwerów, bo każdy plugin może wołać inny serwer.

Kiedyś ClientSession miał swój własny event loop (pochodzący z connectora), więc jedna sesja obsługuje asynchronicznie wszystkie żądania. To jest plus. Czyli jeden serwer dc nie potrzebuje wielu sesji. Bo tak czy inaczej, jedna sesja obsłuży wiele pluginów na spokojnie. Dobrze. Teraz pytanie, czy jeśli stworzę więcej sesji, to bot będzie równomiernie obsługiwał każdy serwer - tzn. wolę, aby program poświęcał tyle samo czasu każdemu serwerowi dc, a nie, że jedna sesja ma szansę obsługiwać przez długi czas pluginy tylko z jednego serwera.

Czyli każdy serwer dc dostanie własną sesję. Ok.

Podsumowując:
- obsługuję każdy serwer
- każdy serwer ma swoją sesję w aiohttp, przekazywaną wybranym pluginom
- każda instancja pluginu ma swoją konfigurację, każdy task również
- przechowuję jakiś json - zbiór tasków - każdemu przypisuję plugin, okres z którym ma być wykonywany, kanał na którym mają się pojawić wiadomości, listę wzmianek, a także dane: czyli argumenty dla metody, która ma zwrócić listę wiadomości (np. link do strony forum z którego biorę posty)
- komendy bota:
    - dodaj nowy task
    - skasuj task
    - edytuj task
    - wyświetl taski (a kiedyś może czas, który musi minąć przed następnym wywołaniem taska)
    - wykonaj task (bo nie chce mi się czekać)
- taski mogą mieć swoje numerki, umieściłbym je w liście
- zastanawiam się, czy chcę mieć jakąś osobną klasę dla bota, by wykonywać rzeczy dla konkretnego serwera - tzn. jeśli bot wykryje komendę od serwera A, to przekaże to klasie serwera A. Może dzięki temu będę zapisywał konfigurację dla konkretnego serwera. Czyli np. listę tasków, zbiór uruchomionych pluginów. Na pewno będzie mniejszy chaos. Bo będę miał pewność, że to, co miało zostać zrobione na serwerze A, zostanie NA PEWNO zrobione na serwerze A. Czyli w razie czego będę mógł łatwo zrobić logi dla konkretnego serwera (bo każdemu serwerowi przypiszę osobny plik z logami). A także każdy serwer będzie miał osobną historię.

Dobra, a jak chcę zrealizować taski? Wiem, że istnieją dekoratory. Ale tutaj ilość tasków może się zmieniać, a także ich treść. Nie chcę za każdym razem definiować funkcji. Bo tutaj task to po prostu wywołanie metody .dejwiadomości() na pluginie i użycie jakichś tam argumentów.

W przyszłości mógłbym dodać kod odpowiadający za dodanie nowego serwera do bota - albo i nie - po prostu trzymam globalną listę serwerów i jeśli pojawi się wiadomość, której serwer nie ma swojego obiektu dla tasków, to dotworzę nowy.

Podsumowanie z 0:09 26.06
Mam już stworzoną klasę TaskHandler i podstawowe komendy dla bota. Niektóre (jak run_task i edit_task) są nieukończone. Te metody, które już zaimplementowałem, pracują na liście słowników z danymi danego tasku. Chcę zachować te dane, ale też chcę przechowywać listę tasków-obiektów (stworzonych dekoratorem dc.ext.loop), które mogę zaczynać i kończyć. Chcę też jakoś zgrabnie stworzyć sesję http dla każdego TaskHandlera, a nie wiem, czy dam radę tak łatwo dodawać i usuwać je z kolejki z contextlib. Wtedy nie wiem też gdzie wpakować tą kolejkę z contextlib. Można by się pokusić o umieszczenie jej nad całym botem. Albo, na przykład, stworzyć bota, który dziedziczy po command.Bot i którego da się otworzyć w kontekst managerze. A w tym managerze umieścić kolejkę z contextliba. Cóż. Nie mam czasu i chęci teraz o tym myśleć, ale pewnie zabiorę się za to jutro.
Trzeba zajrzeć do plugins.py, bo jest tam burdel.

Póki nie zaimplementuję własnego ExitPoola do contextlib, to alternatywą jest ExitStack. Ale on nie pozwala mi usunąć sesji, która jest gdzieś w środku. Musiałbym wszystkie pozamykać i stworzyć na nowo. W skrócie (bo pewnie poczytam o tym więcej) - ExitStack kopiuje działanie zagnieżdżonych context managerów - czyli działa jak stos. Nie masz dostępu do managera gdzieś w środku.

Nie wiem co zrobić z sesją. Tzn. jak ją mam obsługiwać. Jestem pewny, że TaskHandler potrzebuje własnej sesji dla requestów. Teraz pytanie, w jak mądry sposób mam to zrobić. Nie wiem jak stworzyć sesję na czas działania obiektu. Może ją wpakować do aenter i aclose? 

# Podsumowanie z 26.06, 23:11
- ~~Nie wiem gdzie upchać to ClientSession. Ale kod przynajmniej działa dla najprostszych pluginów, bez http. To jest jakiś tam sukces. Jeśli zadziała dla pluginu http, a poza tym będzie sobie robił jakieś podstawowe kopie zapasowe, to osiągnę MVP. Jakby co, to dodawanie nowych stron robi się u mnie przez przekazanie strony do pluginu, przez kwargs. No i zmieniło się trochę moje podejście - teraz istnieje jedna instancja pluginu dla każdego linku (bo założyłem, że będę chciał je konfigurować).~~
- mam metodę prepare_messages. Przeniosę ją do Plugin, a w TaskHandler (mogę zmienić nazwę na TaskManager) zostawić kod odpowiedzialny za np. dodawanie wzmianek
- wiadomości mają być wysyłane blokami (czyli cała lista wiadomości z taska nie może zostać przerwana) - zamierzam stworzyć klasę do wysyłania wiadomości, jakiegoś average consoomera z kolejką

# Sesja

Dobra. To co z ClientSession? On wymaga, by go otworzyć context managerem. A gdzie taki mogę wpakować? Próbowałem w:
- klasie Bot:
    - problem w tym, że nie wiem, jak to wziąć pod uwagę. Problem jest taki, że session.aclose() to coroutine. Czyli nie mogę tego trzymać w Bot, bo ta klasa odpala główną pętlę. Czyli jak chcę, by sesje były używane przez TaskHandlery, to muszą być poodpalane nad nimi (TaskHandler może być wykorzystywany jako menedżer kontekstu, albo jego istnienie może być zamknięte w menedżerze.
    - co jeśli sesja będzie nad komendami? - byłaby jedna coroutine, która rejestrowałaby komendy. Jej kod byłby wykonywany w context managerze - ExitStack dla TaskHandlerów. Ona by odpowiadała za sprawdzenie, z jakiego serwera poszła komenda i przydzielała by jej odpowiadającego serwerowi TaskHandlera. Teraz pytanie, w jaki sposób mogę napisać coś, co nasłuchuje samą komendę.
- klasie TaskHandler

Dobra, rozwiązałem to dziwnie - TaskHandler da się uruchomić w context managerze (wtedy otwiera się sesja) - robię to przy tworzeniu tasku. Gdy task zostanie skasowany, handler wyjdzie z sesji. Teraz sprawdzę, czy ta sama sesja tworzy się dla wielu tasków...

...no niestety nie.

A jednak tak. Tylko trzeba było dodać *args do aexit i sprawdzanie, czy sesja jest tworzona pierwszy raz.

Program zachowuje się dziwnie. Tworzy sesję, po czym ją zamyka, ale przekazuje taskowi. Nie wiem, czy nie lepiej będzie, menedżer kontekstu wpakować do samego taska. Wtedy sesja będzie zamykana i otwierana za każdym razem, kiedy odpala się task. Co w sumie... Jest dość słabym zachowaniem, bo chciałem, by sesja działała cały czas. Albo nie wiem. Nie wiem właściwie.

Jakbym chciał użyć autocomplete, to mogę użyć biblioteki interactions (do botów ze slashem "/"), zdaje się że nie różni się to bardzo niż pisanie normalnego bota (wciąż mogę zrobić klasę bota i większość rzeczy będzie zachowanych, ale bot będzie pochodził z interactions, a nie commands)

# Podsumowanie 27.06 17:36
Taski mogą korzystać ze sesji. Moje obecne todo:

- zastanowić się nad reprezentacją danych tasków (np. czy mam je od razu pakować do wspólnego pliku czy może do osobnych, no i kiedy mam zaglądać do tego pliku - czy dane mają zalegać w pamięci?)
- po tym powyżej, trzeba naprawić moduł z pluginami (są teraz inne założenia - wiele obiektów z własną konfiguracją zamiast jednego przyjmującego zadania) no i zaimplementować tam przygotowywanie wiadomości do wysłania (można wymyślić interfejs/metodę, gdzie będę dawał jakieś flagi w parametrach, np. czy mam podzielić wiadomość na części, czy wysłać jako plik, a wtedy jakie ma być jego rozszerzenie)
- average consoomer - task ma wysyłać listy wiadomości do consoomera, a on ma je wysyłać blokami (by zachować kolejność między taskami)
- można się zastanowić nad przeniesieniem się na bibliotekę interactions, bo wolałbym się dać pochlastać, niż pisać ręcznie komendy.

Po skończeniu todo, będę miał prawdopodobnie mvp. Tylko trzeba zintegrować bota z pluginami. Po osiągnięciu mvp, mogę założyć repo, ale jeszcze nie podeślę go na githuba.

# 9.07.22
- ~~sprawdzić, jak wygląda json z taskiem (testowanie); mogę przechowywać osobno konfigurację handlera i listę tasków~~
- ~~przerobić create_task (by mieć listę pluginów)~~
- ~~każde osobne zadanie TaskHandlera można oddelegować do klas (sender, logger)~~ ~~został tylko sender na razie, logger wymaga zbyt dużo danych od Handlera, by był osobną klasą~~ Jeśli klasa jest ogólna ("interfejs"), to może zlecać zadania bardziej konkretnym ("sender", "logger", "producer")
- sprawdzić obecny kod, zwłaszcza przesyłanie danych do pluginów
- obsłużyć najważniejsze wyjątki
- dokumentacja
- napisać testowy plugin http oparty o jakąś stronę - poligon
- naprawić plugin do wota
- slash commands?
- poczytać o bibliotekach do testów i materiały od Boryczko o internecie

# 11.07.22
- przekazywanie argumentów do pluginu (myślę o dodatkowej komendzie
lub liście/słowniku z obiektami Option())
- naprawienie pluginów
- wyjątki
- podpowiedzi do komend
- dokumentacja (komentarze + komenda help)

# 13.07.22
Pracuję nad przekazywaniem argumentów. Sprawa się skomplikowała. W skrócie:
- Bot prosi o argumenty dla komendy create_task
- Ta powinna zależeć od pluginu, którego task tworzymy
(nie da się tworzyć komend w oparciu o (`*args` i `**kwargs`))
- TaskHandler ma dostęp do pluginów, a Bot nie. W takim razie,
Bot nie powinien tworzyć komend w zależności od użytego Pluginu, a jeśli
tak, to nie może podpowiadać i walidować tak ładnie argumentów, które są
skrojone pod dany plugin
- Zdecydowałem się użyć Modala - po komendzie, jeśli jest to potrzebne,
Bot powinien zapytać w ładnym formsie o dodatkowe dane. Problem polega na tym,
by jakoś ładnie to zaprojektować.
- No to tak:
	1. Bot wysyła komendę i przekazuje podstawowe dane
	2. TaskHandler tworzy zadanie, ale zauważa, że Plugin potrzebuje danych,
	rzuca wyjątek
	3. Bot obsługuje wyjątek: wykonuje coś w stylu handler.plugin_data() -
	tyle, że pass_data() powinno sprawdzić Plugin.modal i wykonać Plugin():
		```py
		class TaskHandlerNew(TaskHandler):
			""" Poprawiony TaskHandler """
			def plugin_modal(self, plugin: Plugin):
				return Plugin.modal				
			def create_task(self, *args):
				...
				# tu powinienem stworzyć taska mając już *args
		```
- bota nie powinno obchodzić, do czego służą te argumenty - zakładam,
że po prostu dodaje formsa na twarz i prośbę, by go odpalić (**tu pojawia się
myśl: co jeśli plugin prosi o argumenty w inny sposób...?**)
- w skrócie, może Bot powinien oferować pewien prosty interfejs dla
TaskHandlera, np. "wyślij formsa i dej wynik", "wylistuj mi userów",
"sprawdź czy typ ma uprawnienia". TaskHandler będzie próbował robić rzeczy
z użyciem Pluginów, a jeśli napotka potrzebę, to spyta Bota. A jak spyta...?
Myślałem właśnie o wyjątkach, które zwracają jakieś polecenie, kod czy coś.
Ewentualnie wyjątek powoduje wejście w tryb, w którym to Bot wykonuje prośby
TaskHandlera do momentu, gdy ten przestanie go prosić o dalszą pomoc i skończy
robotę - **nie wiem, czy to będzie funkcjonalne**

- Kolejna myśl: nie muszę używać "channel" jako argumentu - wystarczy użyć
komendy na tym konkretnym kanale, bo nie będzie mi śmiecić - Bot ją usunie,
a jego odpowiedź będzie tak czy siak niewidzialna (?), a nawet jak nie, to
i tak ją usunie

# 14.07.22
- Jeszcze raz: TaskHandler próbuje wywołać Plugin(arguments=None), nie może
(bo dostał wyjątek), więc **powinien** zwrócić się do Bota o argumenty,
a nie sam je zdobywać. Bo mi się mieszają zadania w klasach - choć dawno to
się stało
- w skrócie, TaskHandler tworzy taska, ale moim zdaniem, Sender powinien mieć
dostęp do bota

Czyli TaskHandler tworzy taski, ale nie powinien nic wysyłać na czacie,
powinien robić to Bot, który posiłkuje się Senderem
