#!/usr/bin/env python3
"""Common deterministic FOS construction and linkage-recovery metrics."""
from __future__ import annotations
import math

import numpy as np
from sklearn.metrics import mutual_info_score


def average_linkage_fos(n_variables, edges, threshold=0.0):
    clusters = [(index,) for index in range(n_variables)]
    fos = list(clusters)
    while len(clusters) > 1:
        best = None
        best_value = -math.inf
        for left_index, left in enumerate(clusters):
            for right_index in range(left_index + 1, len(clusters)):
                right = clusters[right_index]
                weights = [
                    float(edge["weight"]) for edge in edges
                    if edge.get("selected", False)
                    and edge.get("supported", False)
                    and float(edge["weight"]) > 0
                    and np.isfinite(edge["weight"])
                    and float(edge["weight"]) >= threshold
                    and ((edge["i"] in left and edge["j"] in right)
                         or (edge["j"] in left and edge["i"] in right))
                ]
                if not weights:
                    continue
                value = float(np.mean(weights))
                pair = (left, right)
                if value > best_value + 1e-14 or (
                    abs(value - best_value) <= 1e-14
                    and best is not None and pair < best
                ):
                    best = pair
                    best_value = value
        if best is None:
            break
        left, right = best
        merged = tuple(sorted(left + right))
        fos.append(merged)
        clusters = [cluster for cluster in clusters if cluster not in best]
        clusters.append(merged)
        clusters.sort()
    return fos


def pair_cocluster_matrix(fos, n_variables):
    matrix = np.zeros((n_variables, n_variables), dtype=bool)
    for subset in fos:
        for left in subset:
            for right in subset:
                if left != right:
                    matrix[left, right] = True
    return matrix


def pair_cocluster_metrics(true_fos, predicted_fos, n_variables):
    true_matrix = pair_cocluster_matrix(true_fos, n_variables)
    predicted_matrix = pair_cocluster_matrix(predicted_fos, n_variables)
    indices = np.triu_indices(n_variables, 1)
    truth = true_matrix[indices]
    predicted = predicted_matrix[indices]
    tp = int(np.sum(truth & predicted))
    fp = int(np.sum(~truth & predicted))
    fn = int(np.sum(truth & ~predicted))
    tn = int(np.sum(~truth & ~predicted))
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": float(precision), "recall": float(recall),
        "f1": float(2 * precision * recall / max(precision + recall, 1e-15)),
        "false_merge_rate": float(fp / max(fp + tn, 1)),
    }


def linkage_partition(n_variables, edges):
    parent = list(range(n_variables))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for edge in edges:
        left = find(int(edge["i"]))
        right = find(int(edge["j"]))
        if left != right:
            parent[right] = left
    labels = [find(index) for index in range(n_variables)]
    mapping = {}
    for index, label in enumerate(labels):
        mapping.setdefault(label, index)
    return [mapping[label] for label in labels]


def partition_entropy(labels):
    counts = np.bincount(np.asarray(labels, dtype=int))
    probabilities = counts[counts > 0] / len(labels)
    return float(-np.sum(probabilities * np.log(probabilities)))


def variation_of_information(true_labels, predicted_labels):
    mutual_information = mutual_info_score(true_labels, predicted_labels)
    return float(partition_entropy(true_labels) + partition_entropy(predicted_labels)
                 - 2 * mutual_information)
