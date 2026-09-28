import time, pandas as pd
from textblob import TextBlob
from colorama import init, Fore

init(autoreset=True)

# ---------------- LOAD DATA ----------------
try:
    df = pd.read_csv("imdb_top_1000.csv")
except FileNotFoundError:
    print(Fore.RED + "Error: The file 'imdb_top_1000.csv' was not found.")
    raise SystemExit

genres = sorted({g.strip() for xs in df["Genre"].dropna().str.split(", ") for g in xs})
watchlist = []

def dots():
    for _ in range(3):
        print(Fore.YELLOW + ".", end="", flush=True)
        time.sleep(0.5)

def senti(p):
    return "Positive 😊" if p > 0 else "Negative 😞" if p < 0 else "Neutral 😐"

def get_genre():
    print(Fore.GREEN + "Available Genres: ")
    for i, g in enumerate(genres, 1):
        print(f"{Fore.CYAN}{i}. {g}")
    print()
    while True:
        x = input(Fore.YELLOW + "Enter genre number or name: ").strip()
        if x.isdigit() and 1 <= int(x) <= len(genres):
            return genres[int(x) - 1]
        x = x.title()
        if x in genres:
            return x
        print(Fore.RED + "Invalid input. Try again.\n")

def get_rating():
    while True:
        x = input(Fore.YELLOW + "Enter minimum IMDB rating (7.6-9.3) or 'skip': ").strip()
        if x.lower() == "skip":
            return None
        try:
            r = float(x)
            if 7.6 <= r <= 9.3:
                return r
            print(Fore.RED + "Rating out of range. Try again.\n")
        except ValueError:
            print(Fore.RED + "Invalid input. Try again.\n")

def pick_movies(genre=None, rating=None, mp=None, n=5):
    d = df
    if genre:
        d = d[d["Genre"].str.contains(genre, case=False, na=False)]
    if rating is not None:
        d = d[d["IMDB_Rating"] >= rating]
    d = d.dropna(subset=["Overview"])
    if d.empty:
        return []

    d = d.sample(min(len(d), 40))          # random pool = fresh results each time
    movies = []
    for _, r in d.iterrows():
        pol = TextBlob(r["Overview"]).sentiment.polarity
        match = None
        if mp is not None:                 # how close is the movie's mood to the user's?
            match = round((1 - abs(mp - pol) / 2) * 100)
        movies.append({"title": r["Series_Title"], "genre": r["Genre"],
                       "rating": r["IMDB_Rating"], "pol": pol,
                       "match": match, "overview": r["Overview"]})

    if mp is not None:
        movies.sort(key=lambda m: m["match"], reverse=True)   # best match first
    return movies[:n]

def show_cards(movies):
    for i, m in enumerate(movies, 1):
        print(f"\n{Fore.CYAN}{i}. 🎥 {m['title']}")
        print(f"   🎭 Genre: {m['genre']}")
        print(f"   {'⭐' * round(m['rating'] / 2)}  IMDB: {m['rating']}")
        print(f"   💬 Overview mood: {senti(m['pol'])} ({m['pol']:.2f})")
        if m["match"] is not None:
            filled = m["match"] // 10
            print(f"   💘 Mood match: {'█' * filled}{'░' * (10 - filled)} {m['match']}%")
        print(f"   📖 {m['overview'][:100]}...")

def save_to_watchlist(movies):
    x = input(Fore.YELLOW + "\nSave one to your watchlist? Enter its number or 'skip': ").strip()
    if x.isdigit() and 1 <= int(x) <= len(movies):
        title = movies[int(x) - 1]["title"]
        if title not in watchlist:
            watchlist.append(title)
        print(Fore.GREEN + f"✅ Added '{title}' to your watchlist!")


print(Fore.BLUE + "🎥 Welcome to your Personal Movie Recommendation Assistant! 🎥\n")
name = input(Fore.YELLOW + "What's your name? ").strip()
print(f"\n{Fore.GREEN}Great to meet you, {name}!\n")

mood = input(Fore.YELLOW + "How do you feel today? (Describe your mood): ").strip()
print(Fore.BLUE + "\nAnalyzing mood", end="", flush=True); dots()
mp = TextBlob(mood).sentiment.polarity
md = "positive 😊" if mp > 0 else "negative 😞" if mp < 0 else "neutral 😐"
print(f"\n{Fore.GREEN}Your mood is {md} (Polarity: {mp:.2f}).\n")

while True:
    print(Fore.BLUE + "\n=== MENU ===")
    print(Fore.CYAN + "1. 🤖 AI Mood Pick (genre + rating + mood match)")
    print(Fore.CYAN + "2. 🎲 Surprise Me (totally random)")
    print(Fore.CYAN + "3. 📋 View my watchlist")
    print(Fore.CYAN + "4. 👋 Quit")
    choice = input(Fore.YELLOW + "Choose 1-4: ").strip()

    if choice == "1":
        genre = get_genre()
        rating = get_rating()
        print(f"{Fore.BLUE}\nFinding movies for {name}", end="", flush=True); dots()
        movies = pick_movies(genre, rating, mp)
    elif choice == "2":
        print(f"{Fore.BLUE}\nRolling the dice", end="", flush=True); dots()
        movies = pick_movies(n=1)
    elif choice == "3":
        if watchlist:
            print(Fore.GREEN + "\n📋 Your Watchlist:")
            for i, t in enumerate(watchlist, 1):
                print(f"{Fore.CYAN}{i}. {t}")
        else:
            print(Fore.RED + "\nYour watchlist is empty.")
        continue
    elif choice == "4":
        break
    else:
        print(Fore.RED + "Invalid choice. Try again.")
        continue

    if not movies:
        print(Fore.RED + "\nNo suitable movie recommendations found.")
        continue
    show_cards(movies)
    save_to_watchlist(movies)

print(Fore.GREEN + f"\nEnjoy your movie picks, {name}! 🎬🍿")
if watchlist:
    print(Fore.YELLOW + "Don't forget to watch: " + ", ".join(watchlist) + "\n")