# Validation supplement

*An OWL 2 Object-Property Cheat Sheet* — KGSWC 2026, submission 9.

## Run

Requires Python 3 and JDK 17. Download the official ROBOT 1.9.10 dependency bundle separately:

https://github.com/ontodev/robot/releases/download/v1.9.10/robot.jar

From this directory, run:

```sh
python3 run_turtle_checks.py --jar /absolute/path/to/robot.jar
```

The script verifies the dependency checksum and writes fresh output to `reproduced/`. For another run, add `--output another_directory`. It exits nonzero on mismatches or execution errors. The supplied `results/` directory contains a recorded run and its environment, versions, source hashes, and diagnostics. The JAR is not redistributed here.

## Files

- `examples/`: 53 base Turtle test ontologies.
- `queries/`: 24 Turtle query containers, kept separate from test inputs.
- `nonempty/`: 17 additional pairwise tests with a positive property assertion.
- `owl_tasks.tsv` and `nonempty/owl_tasks.tsv`: expected profile, consistency, and entailment outcomes.
- `RunOwlChecks.java` and `run_turtle_checks.py`: executable checks.
- `results/`: observed results, configuration/environment summary, and one combined console log.

## Results and interpretation

OWLAPI 4.5.29 checks OWL 2 DL membership. HermiT artifact 1.4.5.456 (API-reported version 1.4.1.432) checks consistency and entailment using factory defaults, no explicit precomputation, and a 1 GiB Java heap.

| Suite | Recorded outcome |
| --- | --- |
| Base 53 cases | 47 admissible; six outside OWL 2 DL |
| Consistency of admissible base cases | 42 consistent; five inconsistent |
| Queries | 12 entailed; 12 not entailed |
| Additional 17 positive-assertion tests | 14 consistent; three inconsistent |
| Mismatches or execution errors | Zero |

PASS means agreement with the expected outcome; some correct outcomes are inconsistency or profile rejection. Out-of-profile inputs are not sent to HermiT. The additional tests distinguish a property that may be nonempty from one forced to be empty. No distinctness of individual names is assumed.

The base cases comprise 21 pairwise, 14 hierarchy, 14 selected seeded, and four structural examples. The tests do not cover every row of the manuscript's 28-row seeded table and do not establish scalability, comparative reasoner performance, user benefit, or correctness of the original ATM system.

For B subproperty A, symmetry and transitivity on B do not entail those characteristics on A; only local inferred pairs transfer upward. Non-entailment of a positive assertion is also different from entailment of its negation. The manuscript must preserve these distinctions.

Expectations follow the OWL 2 Direct Semantics and Structural Specification, sections 11.1–11.2:
https://www.w3.org/TR/owl2-direct-semantics/
https://www.w3.org/TR/owl2-syntax/

The examples/scripts were prepared with ChatGPT assistance and executed as recorded. Authors should review and adopt the supplement. This archive contains Turtle versions of the examples; the manuscript should describe them as Turtle rather than functional-syntax documents.
