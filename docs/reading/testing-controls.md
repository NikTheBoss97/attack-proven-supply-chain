<!-- Author: Nicola Antonello -->

# Testing controls

How to show that a test, or a control, really does what it claims. Part of the [reading list](README.md).

## Breaking things on purpose

- ★ Goran Petrović et al., [Does Mutation Testing Improve Testing Practices?](https://doi.org/10.1109/ICSE43902.2021.00087) (ICSE, 2021). A study of almost 15 million mutants: developers who use mutation testing write more tests, and the mutants they leave behind are coupled with real faults.
- Datadog, [Stratus Red Team](https://stratus-red-team.cloud/) (documentation). Attack techniques for cloud platforms and Kubernetes, built to validate that detections work.
- Y. Jia, M. Harman, [An Analysis and Survey of the Development of Mutation Testing](https://doi.org/10.1109/TSE.2010.62) (IEEE Transactions on Software Engineering, 2011). The survey of the field.
- R. A. DeMillo, R. J. Lipton, F. G. Sayward, [Hints on Test Data Selection: Help for the Practicing Programmer](https://doi.org/10.1109/C-M.1978.218136) (IEEE Computer, 1978). The origin of mutation testing, and of the coupling effect: tests that catch simple errors also tend to catch complex ones.

## Test doubles

- Davide Spadini et al., [To Mock or Not to Mock? An Empirical Study on Mocking Practices](https://doi.org/10.1109/MSR.2017.61) (MSR, 2017). Which dependencies developers replace with mocks and why: they mock what makes testing hard, avoid mocking classes that hold the system's rules, and find it hard to keep a mock faithful to the real class.
