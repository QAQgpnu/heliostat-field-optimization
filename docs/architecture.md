# Architecture

```text
CSV or generated layout
        |
        v
MirrorLayout validation ---- SiteConfig / ReceiverConfig
        |                              |
        +--------------+---------------+
                       v
              60 annual sample times
                       |
          +------------+-------------+
          |            |             |
      solar/DNI   mirror normals   neighbour cache
          |            |             |
          +------------+-------------+
                       v
      cosine * shadow/blocking * atmosphere * truncation * reflectivity
                       |
                       v
         per-mirror power -> field and specific-power summaries
                       |
              figures / CSV / JSON
```

The optimization module calls the same simulation path for every candidate. There is no separate “presentation” formula and no hard-coded target output.
