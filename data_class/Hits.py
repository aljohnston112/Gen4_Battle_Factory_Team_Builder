from attrs import frozen


@frozen
class Hits:
    hits_taken: float
    hits_given: float