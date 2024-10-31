from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from ..extractor.component_extractor import UIPattern
import re


@dataclass
class PatternVersion:
    timestamp: datetime
    complexity_score: float
    usage_count: int
    variations: List[str]
    template_structure: str
    associated_styles: Dict[str, str]


@dataclass
class PatternProfile:
    pattern_id: str
    versions: List[PatternVersion]
    common_combinations: List[str]
    optimization_suggestions: List[str]


class PatternProfiler:
    def __init__(self):
        self.profiles = {}
        self.current_timestamp = datetime.now()

    def profile_patterns(self, pattern_registry: Dict[str, List[UIPattern]]) -> Dict[str, PatternProfile]:
        """Profiles patterns and tracks their evolution"""
        for pattern_id, patterns in pattern_registry.items():
            if pattern_id not in self.profiles:
                self.profiles[pattern_id] = PatternProfile(
                    pattern_id=pattern_id, versions=[], common_combinations=[], optimization_suggestions=[]
                )

            # Calculate current metrics
            complexity_score = self._calculate_complexity(patterns)
            usage_count = len(patterns)
            variations = [p.template_structure for p in patterns]

            # Update version history
            self._update_history(
                pattern_id=pattern_id,
                complexity_score=complexity_score,
                usage_count=usage_count,
                variations=variations,
                template_structure=patterns[0].template_structure,
                associated_styles=patterns[0].associated_styles,
            )

            # Update optimization suggestions
            self._update_optimization_suggestions(pattern_id, patterns)

        return self.profiles

    def _update_history(
        self,
        pattern_id: str,
        complexity_score: float,
        usage_count: int,
        variations: List[str],
        template_structure: str,
        associated_styles: Dict[str, str],
    ):
        """Updates version history for a pattern"""
        version = PatternVersion(
            timestamp=self.current_timestamp,
            complexity_score=complexity_score,
            usage_count=usage_count,
            variations=variations,
            template_structure=template_structure,
            associated_styles=associated_styles,
        )
        self.profiles[pattern_id].versions.append(version)

    def _calculate_complexity(self, patterns: List[UIPattern]) -> float:
        """Calculates overall complexity score for a pattern group"""
        if not patterns:
            return 0.0

        total_complexity = 0.0
        for pattern in patterns:
            # Calculate based on template structure
            nesting_depth = pattern.template_structure.count('<')
            directive_count = len(re.findall(r'\*ng[A-Za-z]+', pattern.template_structure))
            style_complexity = sum(len(rules.split(';')) for rules in pattern.associated_styles.values())

            pattern_complexity = (nesting_depth * 0.4 + directive_count * 0.3 + style_complexity * 0.3) / 10
            total_complexity += pattern_complexity

        return total_complexity / len(patterns)

    def _update_optimization_suggestions(self, pattern_id: str, patterns: List[UIPattern]):
        """Updates optimization suggestions for a pattern"""
        suggestions = []
        complexity = self._calculate_complexity(patterns)

        if complexity > 0.7:
            suggestions.append(
                {'message': 'High complexity detected', 'suggestion': 'Consider breaking down into smaller components'}
            )

        if len(patterns) > 10:
            suggestions.append(
                {
                    'message': 'Multiple variations detected',
                    'suggestion': 'Consider standardizing pattern implementation',
                }
            )

        self.profiles[pattern_id].optimization_suggestions = suggestions

    def _analyze_pattern_quality(self, pattern: UIPattern) -> Dict[str, Any]:
        return {
            'accessibility': {
                'score': self._check_accessibility(pattern),
                'issues': self._identify_accessibility_issues(pattern),
            },
            'maintainability': {
                'score': self._calculate_maintainability_score(pattern),
                'factors': self._identify_maintainability_factors(pattern),
            },
            'performance': {
                'score': self._evaluate_performance(pattern),
                'optimizations': self._suggest_optimizations(pattern),
            },
            'best_practices': {
                'adherence': self._check_best_practices(pattern),
                'violations': self._identify_violations(pattern),
            },
        }
