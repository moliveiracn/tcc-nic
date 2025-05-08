def generate_pairwise_queries(hobbies, demeaning_words):
    """
    Generate one search query per (hobby, demeaning_word) pair, e.g.:
      '"knitting" "dumb"' 
    """
    queries = []
    for hobby in hobbies:
        for word in demeaning_words:
            # wrap each term in quotes to ensure exact‐phrase matching
            q = f'"{hobby}" "{word}"'
            queries.append(q)
    return queries

def generate_grouped_queries(hobbies, demeaning_words):
    """
    Generate one query per hobby, grouping all demeaning words with OR, e.g.:
      '"knitting" ("dumb" OR "pointless" OR "silly")'
    """
    # pre-build the OR‐joined demeaning clause once
    de_clause = " OR ".join(f'"{w}"' for w in demeaning_words)
    queries = [f'"{hobby}" ({de_clause})' for hobby in hobbies]
    return queries

# if __name__ == "__main__":
#     # Example keyword lists
#     female_dominated = ["knitting", "baking", "scrapbooking"]
#     male_dominated   = ["woodworking", "fishing", "gaming"]
#     demeaning        = ["dumb", "pointless", "silly", "waste of time"]

#     # Generate pairwise queries
#     pw_queries = generate_pairwise_queries(female_dominated + male_dominated, demeaning)
#     print("Pairwise queries:")
#     for q in pw_queries:
#         print(q)

#     # Or generate grouped queries (one per hobby)
#     gp_queries = generate_grouped_queries(female_dominated + male_dominated, demeaning)
#     print("\nGrouped queries:")
#     for q in gp_queries:
#         print(q)

#     # (Optionally) write to file for your scraper:
#     with open("twitter_queries.txt", "w", encoding="utf-8") as f:
#         for q in pw_queries:
#             f.write(q + "\n")
