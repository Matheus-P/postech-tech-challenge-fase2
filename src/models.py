"""Definição dos modelos candidatos.

Todo o pré-processamento fica dentro do Pipeline: encoder e scaler são
ajustados apenas no fold de treino durante a validação cruzada.
"""

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import (
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from src.config import RANDOM_STATE
from src.preprocessing import CATEGORICAS


def make_preprocessor(numericas: list[str], categoricas: list[str], scale: bool) -> ColumnTransformer:
    """One-hot nas categóricas; padronização nas numéricas só quando pedido."""
    blocos = [("num", StandardScaler() if scale else "passthrough", numericas)]
    if categoricas:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        blocos.append(("cat", encoder, categoricas))
    return ColumnTransformer(blocos, verbose_feature_names_out=False)


def make_pipeline(clf, features: list[str], scale: bool = False) -> Pipeline:
    categoricas = [c for c in features if c in CATEGORICAS]
    numericas = [c for c in features if c not in CATEGORICAS]
    return Pipeline([
        ("prep", make_preprocessor(numericas, categoricas, scale)),
        ("clf", clf),
    ])


def get_models(features: list[str]) -> dict[str, Pipeline]:
    """Modelos candidatos, todos nativos do scikit-learn."""
    rs = RANDOM_STATE
    return {
        "Baseline (taxa média)": make_pipeline(
            DummyClassifier(strategy="prior"), features),
        "Regressão Logística": make_pipeline(
            LogisticRegression(class_weight="balanced", max_iter=2000, random_state=rs),
            features, scale=True),
        "Naive Bayes Gaussiano": make_pipeline(GaussianNB(), features, scale=True),
        "Árvore de Decisão": make_pipeline(
            DecisionTreeClassifier(max_depth=5, min_samples_leaf=50,
                                   class_weight="balanced", random_state=rs),
            features),
        "Random Forest": make_pipeline(
            RandomForestClassifier(n_estimators=300, min_samples_leaf=20,
                                   class_weight="balanced_subsample",
                                   random_state=rs, n_jobs=-1),
            features),
        "Extra Trees": make_pipeline(
            ExtraTreesClassifier(n_estimators=300, min_samples_leaf=20,
                                 class_weight="balanced_subsample",
                                 random_state=rs, n_jobs=-1),
            features),
        "Gradient Boosting (Hist)": make_pipeline(
            HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05,
                                           max_iter=150, l2_regularization=1.0,
                                           class_weight="balanced",
                                           early_stopping=False, random_state=rs),
            features),
    }
