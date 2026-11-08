import csv
import re
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from receipt.config import CATALOG_PATH, EMBEDDING_MODEL, SIMILARITY_THRESHOLD
from receipt.numbers import normalize_text

MAX_WINDOW_WORDS = 5


@dataclass(frozen=True)
class Product:
    id: str
    nombre: str
    categoria: str
    sinonimos: tuple
    unidad: str
    medida: str


@dataclass(frozen=True)
class SynonymMatch:
    product: Product
    start: int
    end: int


def term_regex(term):
    parts = []
    for word in term.split():
        if len(word) > 3 and word.isalpha():
            stem = word[:-1] if word.endswith("s") else word
            parts.append(re.escape(stem) + "(?:es|s)?")
        else:
            parts.append(re.escape(word))
    return r"\s+".join(parts)


class Catalog:
    def __init__(self, products):
        self.products = list(products)
        self.by_id = {product.id: product for product in self.products}
        terms = {}
        for product in self.products:
            for term in (product.nombre, *product.sinonimos):
                terms.setdefault(normalize_text(term), product)
        self.terms = sorted(terms.items(), key=lambda item: -len(item[0]))
        self._patterns = [re.compile(rf"\b{term_regex(term)}\b") for term, _ in self.terms]
        self._term_vectors = None

    def find_all(self, normalized_text):
        found = sorted((SynonymMatch(product, match.start(), match.end())
                        for pattern, (_, product) in zip(self._patterns, self.terms)
                        for match in pattern.finditer(normalized_text)),
                       key=lambda item: (item.start, -item.end))
        clusters = []
        cluster_end = -1
        for item in found:
            if clusters and item.start < cluster_end:
                clusters[-1].append(item)
                cluster_end = max(cluster_end, item.end)
            else:
                clusters.append([item])
                cluster_end = item.end
        winners = [max(cluster, key=lambda item: (item.end, item.end - item.start)) for cluster in clusters]
        seen = set()
        return [item for item in winners if not (item.product.id in seen or seen.add(item.product.id))]

    def find_by_synonym(self, normalized_text):
        matches = self.find_all(normalized_text)
        return matches[0] if matches else None

    def siblings(self, product):
        family = (product.categoria, product.unidad, product.nombre.split()[0])
        return [other for other in self.products
                if other.id != product.id
                and (other.categoria, other.unidad, other.nombre.split()[0]) == family]

    def is_unambiguous(self, normalized_text, product):
        sibling_ids = {sibling.id for sibling in self.siblings(product)}
        if not sibling_ids:
            return True
        sibling_terms = [f" {term} " for term, owner in self.terms if owner.id in sibling_ids]
        for term, owner in self.terms:
            if owner.id != product.id:
                continue
            heard = re.search(rf"\b{term_regex(term)}\b", normalized_text)
            if heard and not any(f" {term} " in sibling_term for sibling_term in sibling_terms):
                return True
        return False

    def vocabulary_prompt(self):
        return "Pedido de ferretería: " + ", ".join(product.sinonimos[0] for product in self.products) + "."

    def match_by_embedding(self, text, threshold=SIMILARITY_THRESHOLD):
        embedder = load_embedder()
        if self._term_vectors is None:
            self._term_vectors = embedder.encode(
                [term for term, _ in self.terms], normalize_embeddings=True, convert_to_numpy=True)
        words = normalize_text(text).split()
        windows = {" ".join(words[i:i + size])
                   for size in range(2, MAX_WINDOW_WORDS + 1)
                   for i in range(len(words) - size + 1)} or {" ".join(words)}
        queries = embedder.encode(sorted(windows), normalize_embeddings=True, convert_to_numpy=True)
        similarity = queries @ self._term_vectors.T
        best_term = int(np.argmax(np.max(similarity, axis=0)))
        score = float(np.max(similarity))
        if score < threshold:
            return None
        return self.terms[best_term][1], score


@lru_cache(maxsize=1)
def load_embedder():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBEDDING_MODEL)


def read_products(path=CATALOG_PATH):
    with open(path, encoding="utf-8", newline="") as handle:
        return [Product(row["id"], row["nombre"], row["categoria"],
                        tuple(part.strip() for part in row["sinonimos"].split("|") if part.strip()),
                        row["unidad"], row["medida"])
                for row in csv.DictReader(handle)]


@lru_cache(maxsize=1)
def load_catalog():
    return Catalog(read_products())
