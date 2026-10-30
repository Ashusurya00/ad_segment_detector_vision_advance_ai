"""
Evaluation metrics: IoU, boundary error, precision, recall, F1.

These operate on lists of (start_s, end_s) segments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SegmentMatch:
    """A matched pair of predicted and ground-truth segments."""
    pred_start: float
    pred_end: float
    gt_start: float
    gt_end: float
    iou: float
    start_error: float  # absolute
    end_error: float    # absolute


@dataclass
class EvalResult:
    """Evaluation result for one video."""
    video_id: str
    gt_count: int
    pred_count: int
    matches: list[SegmentMatch] = field(default_factory=list)
    unmatched_pred: list[tuple[float, float]] = field(default_factory=list)
    unmatched_gt: list[tuple[float, float]] = field(default_factory=list)

    @property
    def precision(self) -> float:
        if self.pred_count == 0:
            return 0.0
        return len(self.matches) / self.pred_count

    @property
    def recall(self) -> float:
        if self.gt_count == 0:
            return 0.0
        return len(self.matches) / self.gt_count

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        if p + r == 0:
            return 0.0
        return 2 * p * r / (p + r)

    @property
    def mean_iou(self) -> float:
        if not self.matches:
            return 0.0
        return sum(m.iou for m in self.matches) / len(self.matches)

    @property
    def mean_boundary_error(self) -> float:
        if not self.matches:
            return 0.0
        errors = [(m.start_error + m.end_error) / 2 for m in self.matches]
        return sum(errors) / len(errors)


def compute_iou(
    pred_start: float, pred_end: float,
    gt_start: float, gt_end: float,
) -> float:
    """
    Compute temporal IoU between two segments.

    IoU = intersection_duration / union_duration
    """
    intersection_start = max(pred_start, gt_start)
    intersection_end = min(pred_end, gt_end)
    intersection = max(0.0, intersection_end - intersection_start)

    union = (pred_end - pred_start) + (gt_end - gt_start) - intersection
    if union <= 0:
        return 0.0
    return intersection / union


def match_segments(
    predictions: list[tuple[float, float]],
    ground_truth: list[tuple[float, float]],
    iou_threshold: float = 0.3,
) -> EvalResult:
    """
    Match predicted segments to ground-truth using greedy IoU matching.

    Each predicted segment is matched to the ground-truth segment with the
    highest IoU, provided it exceeds `iou_threshold`. Each ground-truth
    segment can be matched at most once.

    Args:
        predictions: list of (start_s, end_s) tuples
        ground_truth: list of (start_s, end_s) tuples
        iou_threshold: minimum IoU to consider a match

    Returns:
        EvalResult with matched pairs and unmatched segments
    """
    # Compute all pairwise IoUs
    pairs: list[tuple[float, int, int]] = []
    for pi, (ps, pe) in enumerate(predictions):
        for gi, (gs, ge) in enumerate(ground_truth):
            iou = compute_iou(ps, pe, gs, ge)
            if iou >= iou_threshold:
                pairs.append((iou, pi, gi))

    # Greedy match: highest IoU first
    pairs.sort(key=lambda x: x[0], reverse=True)
    matched_pred: set[int] = set()
    matched_gt: set[int] = set()
    matches: list[SegmentMatch] = []

    for iou, pi, gi in pairs:
        if pi in matched_pred or gi in matched_gt:
            continue
        ps, pe = predictions[pi]
        gs, ge = ground_truth[gi]
        matches.append(SegmentMatch(
            pred_start=ps, pred_end=pe,
            gt_start=gs, gt_end=ge,
            iou=iou,
            start_error=abs(ps - gs),
            end_error=abs(pe - ge),
        ))
        matched_pred.add(pi)
        matched_gt.add(gi)

    unmatched_pred = [predictions[i] for i in range(len(predictions)) if i not in matched_pred]
    unmatched_gt = [ground_truth[i] for i in range(len(ground_truth)) if i not in matched_gt]

    return EvalResult(
        video_id="",
        gt_count=len(ground_truth),
        pred_count=len(predictions),
        matches=matches,
        unmatched_pred=unmatched_pred,
        unmatched_gt=unmatched_gt,
    )
