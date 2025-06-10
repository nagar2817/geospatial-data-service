# Error Details

## Error Message
```
File "/Users/rohitmac/Desktop/data-service-framework-new/app/pipelines/job_discovery/pipeline.py", line 16, in JobDiscoveryPipeline
    NodeConfig(
    ~~~~~~~~~~^
        node=JobScannerNode,
        ^^^^^^^^^^^^^^^^^^^^
        connections=[JobValidatorNode],
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        description="Scan for eligible jobs based on trigger type and criteria"
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ),
    ^
  File "/Users/rohitmac/Desktop/data-service-framework-new/env/lib/python3.13/site-packages/pydantic/main.py", line 253, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/rohitmac/Desktop/data-service-framework-new/env/lib/python3.13/site-packages/pydantic/_internal/_mock_val_ser.py", line 100, in __getattr__
    raise PydanticUserError(self._error_message, code=self._code)
pydantic.errors.PydanticUserError: `NodeConfig` is not fully defined; you should define `BaseNode`, then call `NodeConfig.model_rebuild()`.
```

## Cause
The error occurs due to a **Pydantic forward reference issue**. The `NodeConfig` class references `BaseNode` before it is fully defined, leading to a circular import problem.

## Suggested Fix
1. Ensure that `BaseNode` is fully defined before referencing it in `NodeConfig`.
2. After defining `BaseNode`, call `NodeConfig.model_rebuild()` to resolve the forward reference.

Example:
```python
class BaseNode:
    # Define BaseNode here

NodeConfig.model_rebuild()
```