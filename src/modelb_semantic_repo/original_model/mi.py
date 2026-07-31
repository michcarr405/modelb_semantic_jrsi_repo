"""Compatibility wrappers around the validated revision estimators."""
from ..information import (
    mutual_information,
    conditional_mutual_information,
    corrected_conditional_mutual_information,
    positional_information,
    retained_information,
)


def compute_mutual_information(metabolites, motifs, n_metabolites=4):
    del n_metabolites
    return mutual_information(motifs, metabolites)


def compute_conditional_mutual_information(metabolites, motifs, segments):
    return conditional_mutual_information(motifs, metabolites, segments)
