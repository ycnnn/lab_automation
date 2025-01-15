class Instrument:
    # Class variable shared across all instances
    _params = 123
    def __init__(self):
        pass  # No need to do anything extra in the initializer
        print(self.params + 1)


    @property
    def params(self):
        # Access the class-level _params variable
        return self._params


# Example usage
inst1 = Instrument()
inst2 = Instrument()

# Both instances share the same _params value
print(inst1.params)  # Output: {}

# Modifying params through one instance affects the other