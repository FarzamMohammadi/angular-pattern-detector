from typing import List, Dict, Any, Tuple
from collections import defaultdict
from ..extractor.component_extractor import UIPattern
import re
from ..profiler import PatternProfiler
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
from functools import lru_cache


class PatternAnalyzer:
    def __init__(self):
        self.pattern_registry = defaultdict(list)
        self.similarity_threshold = 0.7  # Configurable similarity threshold
        self.pattern_profiler = PatternProfiler()  # Add profiler
        # Use number of CPU cores for optimal parallelization
        self.max_workers = multiprocessing.cpu_count()

    def _get_pattern_key(self, pattern: UIPattern) -> str:
        """Creates a hashable key from a pattern"""
        return f"{pattern.name}:{hash(pattern.template_structure)}"

    @lru_cache(maxsize=1000)
    def _calculate_complexity_score(self, pattern_name: str) -> float:
        """Cached complexity calculation"""
        patterns = self.pattern_registry[pattern_name]
        if not patterns:
            return 0.0

        total_score = 0.0
        for pattern in patterns:
            template_complexity = self._calculate_template_complexity(pattern)
            style_complexity = self._calculate_style_complexity(pattern)
            logic_complexity = self._calculate_logic_complexity(pattern)

            # Weight the different complexity factors
            total_score += template_complexity * 0.4 + style_complexity * 0.3 + logic_complexity * 0.3

        return total_score / len(patterns)

    @lru_cache(maxsize=1000)
    def _calculate_similarity(self, pattern1: UIPattern, pattern2: UIPattern) -> float:
        """Calculates similarity between two patterns"""
        # Calculate structure similarity
        struct_similarity = self._compare_structures(pattern1.template_structure, pattern2.template_structure)

        # Calculate style similarity
        style_similarity = self._compare_styles(pattern1.associated_styles, pattern2.associated_styles)

        # Weight the similarities
        return struct_similarity * 0.7 + style_similarity * 0.3

    def analyze_patterns(self, patterns: List[UIPattern]) -> Dict[str, Any]:
        """Analyzes patterns using parallel processing"""
        try:
            print("\nStarting pattern analysis...")
            print(f"Input patterns count: {len(patterns)}")

            # Register patterns
            self._register_patterns(patterns)

            print(f"Registered pattern types: {list(self.pattern_registry.keys())}")

            # Create a copy of the registry keys to avoid modification during iteration
            pattern_names = list(self.pattern_registry.keys())

            # Process each pattern type
            pattern_analysis = {}
            for pattern_name in pattern_names:
                print(f"\nAnalyzing pattern type: {pattern_name}")
                pattern_list = self.pattern_registry[pattern_name]
                print(f"Pattern instances: {len(pattern_list)}")

                try:
                    result = self._analyze_single_pattern(pattern_name, pattern_list)
                    if result:
                        pattern_analysis[pattern_name] = result
                        print(f"Analysis complete for {pattern_name}")
                    else:
                        print(f"No analysis results for {pattern_name}")
                except Exception as e:
                    print(f"Error analyzing pattern {pattern_name}: {str(e)}")

            # Generate relationships
            relationships = self._analyze_relationships(pattern_analysis)

            # Create final results
            results = {
                'summary': {
                    'total_patterns_detected': len(patterns),
                    'unique_pattern_types': len(pattern_analysis),
                    'most_common_patterns': self._get_most_common_patterns(),
                },
                'patterns': pattern_analysis,
                'relationships': relationships,
                'recommendations': self._generate_recommendations(pattern_analysis),
            }

            print("\nAnalysis complete:")
            print(f"- Total patterns: {results['summary']['total_patterns_detected']}")
            print(f"- Unique types: {results['summary']['unique_pattern_types']}")
            print(f"- Pattern types: {list(results['patterns'].keys())}")

            return results

        except Exception as e:
            print(f"Error in pattern analysis: {str(e)}")
            import traceback

            print(traceback.format_exc())
            raise

    def _analyze_relationships(self, pattern_analysis: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Analyzes relationships between patterns"""
        relationships = {}
        pattern_names = list(pattern_analysis.keys())

        # Create tasks for each pattern pair
        for i, name1 in enumerate(pattern_names):
            for name2 in pattern_names[i + 1 :]:
                try:
                    relationship = self._analyze_pattern_relationship(name1, name2)
                    if relationship['strength'] > 0:
                        if name1 not in relationships:
                            relationships[name1] = {}
                        relationships[name1][name2] = relationship['strength']
                except Exception as e:
                    print(f"Error analyzing relationship between {name1} and {name2}: {str(e)}")

        return relationships

    def _analyze_single_pattern(self, pattern_name: str, pattern_list: List[UIPattern]) -> Dict[str, Any]:
        """Analyzes a single pattern group"""
        if not pattern_list:
            return {}

        try:
            base_pattern = pattern_list[0]

            return {
                'name': pattern_name,
                'total_usage': len(pattern_list),
                'component_coverage': len(set().union(*[set(p.components) for p in pattern_list])),
                'complexity': self._calculate_complexity_score(pattern_name),
                'accessibility_score': self._calculate_accessibility_score(pattern_list),
                'maintainability_index': self._calculate_maintainability(pattern_list),
                'common_contexts': self._identify_usage_contexts(pattern_list),
                'best_practices_score': self._evaluate_best_practices(pattern_list),
                'variations': self._analyze_variations(pattern_list),
                'template_structure': base_pattern.template_structure,
                'html_structure': base_pattern.html_structure,
                'associated_styles': base_pattern.associated_styles,
                'isolated_template': base_pattern.isolated_template,
                'complexity_breakdown': {
                    'template': self._calculate_template_complexity(base_pattern),
                    'styles': self._calculate_style_complexity(base_pattern),
                    'logic': self._calculate_logic_complexity(base_pattern),
                },
            }
        except Exception as e:
            print(f"Error analyzing pattern {pattern_name}: {str(e)}")
            return {}

    def _generate_summary(self) -> Dict[str, Any]:
        """Generates analysis summary"""
        total_patterns = sum(len(patterns) for patterns in self.pattern_registry.values())
        return {
            'total_patterns_detected': total_patterns,
            'unique_pattern_types': len(self.pattern_registry),
            'most_common_patterns': self._get_most_common_patterns(),
        }

    def _get_most_common_patterns(self) -> List[Dict[str, Any]]:
        """Gets the most frequently occurring patterns"""
        common_patterns = []
        for name, patterns in self.pattern_registry.items():
            common_patterns.append(
                {
                    'name': name,
                    'frequency': len(patterns),
                    'components': len(set().union(*[set(p.components) for p in patterns])),
                }
            )
        return sorted(common_patterns, key=lambda x: x['frequency'], reverse=True)[:5]

    def _analyze_pattern_relationship(self, name1: str, name2: str) -> Dict[str, Any]:
        """Analyzes relationship between two patterns"""
        try:
            pattern1 = self.pattern_registry.get(name1, [None])[0]
            pattern2 = self.pattern_registry.get(name2, [None])[0]

            if not pattern1 or not pattern2:
                return {'strength': 0, 'type': 'none'}

            return {
                'strength': self._calculate_similarity(pattern1, pattern2),
                'type': self._determine_relationship_type(pattern1, pattern2),
            }
        except Exception as e:
            print(f"Error analyzing relationship between {name1} and {name2}: {str(e)}")
            return {'strength': 0, 'type': 'error'}

    def _calculate_template_complexity(self, pattern: UIPattern) -> int:
        """Calculate template complexity percentage"""
        template = pattern.template_structure
        nesting_depth = template.count('<')
        directives = len(re.findall(r'\*ng[A-Za-z]+', template))
        return min(100, (nesting_depth * 5 + directives * 10))

    def _calculate_style_complexity(self, pattern: UIPattern) -> int:
        """Calculate style complexity percentage"""
        styles = pattern.associated_styles
        if not styles:
            return 0
        rules_count = sum(len(rules.split(';')) for rules in styles.values())
        return min(100, rules_count * 5)

    def _calculate_logic_complexity(self, pattern: UIPattern) -> int:
        """Calculate logic complexity percentage"""
        template = pattern.template_structure
        bindings = len(re.findall(r'\{\{[^}]+\}\}', template))
        events = len(re.findall(r'\([^)]+\)=', template))
        return min(100, (bindings * 10 + events * 15))

    def _determine_relationship_type(self, pattern1: UIPattern, pattern2: UIPattern) -> str:
        """
        Determines the type of relationship between two patterns
        """
        if pattern1.html_structure in pattern2.html_structure:
            return 'nested_child'
        elif pattern2.html_structure in pattern1.html_structure:
            return 'nested_parent'
        elif self._calculate_similarity(pattern1, pattern2) > self.similarity_threshold:
            return 'similar'
        return 'co_occurring'

    def _compare_structures(self, struct1: str, struct2: str) -> float:
        """
        Compares two template structures for similarity
        """
        if not struct1 or not struct2:
            return 0.0

        # Normalize structures
        norm1 = re.sub(r'\s+', ' ', struct1).strip()
        norm2 = re.sub(r'\s+', ' ', struct2).strip()

        # Calculate Levenshtein distance
        distance = self._levenshtein_distance(norm1, norm2)
        max_length = max(len(norm1), len(norm2))

        if max_length == 0:
            return 0.0

        return 1 - (distance / max_length)

    def _compare_styles(self, styles1: Dict[str, str], styles2: Dict[str, str]) -> float:
        """
        Compares two sets of styles for similarity
        """
        if not styles1 or not styles2:
            return 0.0

        # Compare selectors and rules
        common_selectors = set(styles1.keys()) & set(styles2.keys())
        if not common_selectors:
            return 0.0

        rule_similarity = sum(self._compare_rules(styles1[sel], styles2[sel]) for sel in common_selectors) / len(
            common_selectors
        )

        return rule_similarity

    def _compare_rules(self, rules1: str, rules2: str) -> float:
        """
        Compares two CSS rule sets for similarity
        """
        rules1_set = set(r.strip() for r in rules1.split(';') if r.strip())
        rules2_set = set(r.strip() for r in rules2.split(';') if r.strip())

        if not rules1_set or not rules2_set:
            return 0.0

        intersection = len(rules1_set & rules2_set)
        union = len(rules1_set | rules2_set)

        return intersection / union

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculates the Levenshtein distance between two strings
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _calculate_nesting_level(self, pattern1: UIPattern, pattern2: UIPattern) -> int:
        """
        Calculates the nesting level between two patterns if they are nested
        """
        if pattern1.html_structure in pattern2.html_structure:
            return pattern2.html_structure.count('<') - pattern1.html_structure.count('<')
        elif pattern2.html_structure in pattern1.html_structure:
            return pattern1.html_structure.count('<') - pattern2.html_structure.count('<')
        return 0

    def _register_patterns(self, patterns: List[UIPattern]) -> None:
        """Registers patterns from all components into the pattern registry"""
        if not patterns:
            print("No patterns to register")
            return

        self.pattern_registry = defaultdict(list)  # Reset registry

        # Process each pattern
        for pattern in patterns:
            try:
                # Get existing pattern names
                existing_pattern_names = list(self.pattern_registry.keys())

                # Check if similar pattern exists
                similar_found = False
                for existing_name in existing_pattern_names:
                    if (
                        self.pattern_registry[existing_name]
                        and self._calculate_similarity(pattern, self.pattern_registry[existing_name][0])
                        > self.similarity_threshold
                    ):
                        self.pattern_registry[existing_name].append(pattern)
                        similar_found = True
                        break

                if not similar_found:
                    self.pattern_registry[pattern.name] = [pattern]

            except Exception as e:
                print(f"Error registering pattern: {str(e)}")
                continue

        print(f"Registered {len(self.pattern_registry)} pattern types")

    def _generate_recommendations(self, pattern_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates recommendations based on pattern analysis
        """
        recommendations = []

        for pattern_name, pattern_data in pattern_analysis.items():
            try:
                # Check pattern complexity
                if pattern_data.get('complexity', 0) > 0.7:
                    recommendations.append(
                        {
                            'pattern': pattern_name,
                            'message': 'High complexity detected',
                            'suggestion': 'Consider breaking down into smaller components',
                            'priority': 'high',
                        }
                    )

                # Check for too many variations
                if len(pattern_data.get('variations', [])) > 5:
                    recommendations.append(
                        {
                            'pattern': pattern_name,
                            'message': 'Multiple variations detected',
                            'suggestion': 'Consider standardizing implementation across components',
                            'priority': 'medium',
                        }
                    )

                # Check for overlapping patterns
                for other_name, other_data in pattern_analysis.items():
                    if pattern_name != other_name:
                        try:
                            # Calculate similarity based on template structures
                            similarity = self._compare_structures(
                                pattern_data.get('template_structure', ''), other_data.get('template_structure', '')
                            )

                            if similarity > self.similarity_threshold:
                                recommendations.append(
                                    {
                                        'pattern': pattern_name,
                                        'message': f'Similar to {other_name}',
                                        'suggestion': 'Consider merging patterns to reduce duplication',
                                        'priority': 'medium',
                                    }
                                )
                        except Exception as e:
                            print(f"Error comparing {pattern_name} with {other_name}: {str(e)}")
                            continue

                # Check maintainability
                if pattern_data.get('maintainability_index', 1.0) < 0.5:
                    recommendations.append(
                        {
                            'pattern': pattern_name,
                            'message': 'Low maintainability score',
                            'suggestion': 'Consider simplifying the pattern structure',
                            'priority': 'high',
                        }
                    )

                # Check accessibility
                if pattern_data.get('accessibility_score', 1.0) < 0.7:
                    recommendations.append(
                        {
                            'pattern': pattern_name,
                            'message': 'Low accessibility score',
                            'suggestion': 'Add proper ARIA attributes and semantic HTML',
                            'priority': 'high',
                        }
                    )

            except Exception as e:
                print(f"Error generating recommendations for {pattern_name}: {str(e)}")
                continue

        return recommendations

    def _calculate_accessibility_score(self, patterns: List[UIPattern]) -> float:
        """
        Calculates accessibility score based on WCAG guidelines and best practices
        """
        if not patterns:
            return 0.0

        total_score = 0.0
        for pattern in patterns:
            # Initialize score components
            score = 0.0
            checks = 0

            # Check for ARIA attributes
            if 'aria-' in pattern.html_structure or 'role=' in pattern.html_structure:
                score += 1
                checks += 1

            # Check for semantic HTML elements
            semantic_elements = ['header', 'nav', 'main', 'article', 'section', 'aside', 'footer']
            for element in semantic_elements:
                if f'<{element}' in pattern.html_structure:
                    score += 1
                    checks += 1

            # Check for form accessibility
            if '<form' in pattern.html_structure:
                if 'aria-label' in pattern.html_structure or 'aria-labelledby' in pattern.html_structure:
                    score += 1
                if '<label' in pattern.html_structure:
                    score += 1
                checks += 2

            # Check for image accessibility
            if '<img' in pattern.html_structure and 'alt=' in pattern.html_structure:
                score += 1
                checks += 1

            # Check for button accessibility
            if '<button' in pattern.html_structure:
                if 'aria-label' in pattern.html_structure or '>' in pattern.html_structure:
                    score += 1
                checks += 1

            # Calculate final score (normalize to 0-1 range)
            pattern_score = score / max(checks, 1)
            total_score += pattern_score

        return total_score / len(patterns)

    def _calculate_maintainability(self, patterns: List[UIPattern]) -> float:
        """
        Calculates maintainability index based on pattern complexity and structure
        """
        if not patterns:
            return 0.0

        total_score = 0.0
        for pattern in patterns:
            # Initialize maintainability factors
            factors = {
                'template_complexity': 0.0,
                'style_complexity': 0.0,
                'binding_complexity': 0.0,
                'isolation_score': 0.0,
            }

            # Calculate template complexity
            template_lines = pattern.template_structure.count('\n') + 1
            nesting_depth = pattern.template_structure.count('<')
            factors['template_complexity'] = 1.0 - min((template_lines * nesting_depth) / 100, 1.0)

            # Calculate style complexity
            style_rules = sum(len(rules.split(';')) for rules in pattern.associated_styles.values())
            factors['style_complexity'] = 1.0 - min(style_rules / 50, 1.0)

            # Calculate binding complexity
            bindings = len(re.findall(r'\{\{[^}]+\}\}|\[(.*?)\]|\((.*?)\)', pattern.template_structure))
            factors['binding_complexity'] = 1.0 - min(bindings / 20, 1.0)

            # Calculate isolation score
            isolation_issues = len(re.findall(r'\{\{[^}]+\}\}', pattern.isolated_template))
            factors['isolation_score'] = 1.0 - min(isolation_issues / 10, 1.0)

            # Calculate weighted average
            weights = {
                'template_complexity': 0.4,
                'style_complexity': 0.2,
                'binding_complexity': 0.2,
                'isolation_score': 0.2,
            }

            pattern_score = sum(score * weights[factor] for factor, score in factors.items())
            total_score += pattern_score

        return total_score / len(patterns)

    def _identify_usage_contexts(self, patterns: List[UIPattern]) -> List[str]:
        """
        Identifies common usage contexts for patterns
        """
        contexts = []

        for pattern in patterns:
            # Check for form context
            if '<form' in pattern.html_structure:
                contexts.append('form')

            # Check for list context
            if '*ngFor' in pattern.html_structure:
                contexts.append('list')

            # Check for navigation context
            if '<nav' in pattern.html_structure or 'routerLink' in pattern.html_structure:
                contexts.append('navigation')

            # Check for modal/dialog context
            if 'modal' in pattern.html_structure.lower() or 'dialog' in pattern.html_structure.lower():
                contexts.append('modal')

            # Check for card/container context
            if 'card' in pattern.html_structure.lower() or pattern.template_structure.count('<div') > 2:
                contexts.append('container')

        # Return unique contexts
        return list(set(contexts))

    def _evaluate_best_practices(self, patterns: List[UIPattern]) -> float:
        """
        Evaluates adherence to Angular and general frontend best practices
        """
        if not patterns:
            return 0.0

        total_score = 0.0
        for pattern in patterns:
            score = 0.0
            checks = 0

            # Check for proper event binding
            if '(click)' in pattern.html_structure:
                score += 1
                checks += 1

            # Check for proper property binding
            if '[' in pattern.html_structure and ']' in pattern.html_structure:
                score += 1
                checks += 1

            # Check for proper structural directives
            if '*ngIf' in pattern.html_structure or '*ngFor' in pattern.html_structure:
                score += 1
                checks += 1

            # Check for proper CSS class usage
            if 'class=' in pattern.html_structure:
                score += 1
                checks += 1

            # Check for proper template structure
            if pattern.template_structure.count('<') < 10:  # Not too deeply nested
                score += 1
                checks += 1

            # Calculate final score
            pattern_score = score / max(checks, 1)
            total_score += pattern_score

        return total_score / len(patterns)

    def _analyze_variations(self, patterns: List[UIPattern]) -> List[Dict[str, Any]]:
        """Analyzes variations of patterns to identify common modifications"""
        if not patterns:
            return []

        variations = []
        base_pattern = patterns[0]

        for pattern in patterns[1:]:
            try:
                variation = {
                    'similarity_score': self._calculate_similarity(base_pattern, pattern),
                    'structural_changes': self._identify_structural_changes(base_pattern, pattern),
                    'style_changes': self._identify_style_changes(base_pattern, pattern),
                    'template': pattern.template_structure,
                }
                variations.append(variation)
            except Exception as e:
                print(f"Error analyzing variation: {str(e)}")
                continue

        return variations

    def _identify_structural_changes(self, pattern1: UIPattern, pattern2: UIPattern) -> List[str]:
        """Identifies structural differences between two patterns"""
        changes = []

        # Compare element structure
        elements1 = re.findall(r'<(\w+)[^>]*>', pattern1.template_structure)
        elements2 = re.findall(r'<(\w+)[^>]*>', pattern2.template_structure)

        if set(elements1) != set(elements2):
            changes.append('element_structure')

        # Compare directives
        directives1 = re.findall(r'\*ng\w+', pattern1.template_structure)
        directives2 = re.findall(r'\*ng\w+', pattern2.template_structure)

        if set(directives1) != set(directives2):
            changes.append('directives')

        # Compare bindings
        bindings1 = re.findall(r'\{\{[^}]+\}\}', pattern1.template_structure)
        bindings2 = re.findall(r'\{\{[^}]+\}\}', pattern2.template_structure)

        if len(bindings1) != len(bindings2):
            changes.append('bindings')

        return changes

    def _identify_style_changes(self, pattern1: UIPattern, pattern2: UIPattern) -> List[str]:
        """Identifies style differences between two patterns"""
        changes = []

        # Compare selectors
        if set(pattern1.associated_styles.keys()) != set(pattern2.associated_styles.keys()):
            changes.append('selectors')

        # Compare rules
        for selector in set(pattern1.associated_styles.keys()) & set(pattern2.associated_styles.keys()):
            if pattern1.associated_styles[selector] != pattern2.associated_styles[selector]:
                changes.append('rules')
                break

        return changes
