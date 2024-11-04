This file is used to track some performance improvements when trying to parse the entire list from merklemap.

This file is 44 gig compressed, and 448 gig uncompressed. Making sure all desired subdomains are read within a single
day is the challenge. Preferably using code that can be somewhat understood.

The final solution uses a lot of optimizations which can be found in the source code. It even uses some anti-patterns
as that is sometimes the best way forward.

merklemap_dns_records_database_25_10_2024.xz is 44 gig compressed
merklemap_dns_records_database_25_10_2024.jsonl is 448 gig uncompressed (x10)

Here are some performance indications processing a million records.

## Uncompressed file, simd json parser, no deque
```
0.0%, 0 records processed, 0 domains added, current time: 2024-11-04 13:04:11.596748, time per iteration: 0.006535 seconds
0.0%, 100,000 records processed, 1090 domains added, current time: 2024-11-04 13:04:12.667657, time per iteration: 1.070894 seconds
0.0%, 200,000 records processed, 2177 domains added, current time: 2024-11-04 13:04:13.742783, time per iteration: 1.075108 seconds
0.01%, 300,000 records processed, 2882 domains added, current time: 2024-11-04 13:04:14.645550, time per iteration: 0.902748 seconds
0.01%, 400,000 records processed, 3532 domains added, current time: 2024-11-04 13:04:15.559011, time per iteration: 0.913445 seconds
0.01%, 500,000 records processed, 4283 domains added, current time: 2024-11-04 13:04:16.470743, time per iteration: 0.911713 seconds
0.01%, 600,000 records processed, 4968 domains added, current time: 2024-11-04 13:04:17.333624, time per iteration: 0.862867 seconds
0.01%, 700,000 records processed, 5675 domains added, current time: 2024-11-04 13:04:18.283722, time per iteration: 0.950083 seconds
0.02%, 800,000 records processed, 6552 domains added, current time: 2024-11-04 13:04:19.289433, time per iteration: 1.005694 seconds
0.02%, 900,000 records processed, 7539 domains added, current time: 2024-11-04 13:04:20.291933, time per iteration: 1.002484 seconds
0.02%, 1,000,000 records processed, 8469 domains added, current time: 2024-11-04 13:04:21.259711, time per iteration: 0.96776 seconds
```

## Live decompression, simd json parser, no deque
```
0.0%, 0 records processed, 0 domains added, current time: 2024-11-04 13:05:22.739336, time per iteration: 0.088093 seconds
0.0%, 100,000 records processed, 1090 domains added, current time: 2024-11-04 13:05:24.226619, time per iteration: 1.48726 seconds
0.0%, 200,000 records processed, 2177 domains added, current time: 2024-11-04 13:05:25.686896, time per iteration: 1.460263 seconds
0.01%, 300,000 records processed, 2882 domains added, current time: 2024-11-04 13:05:26.977237, time per iteration: 1.290323 seconds
0.01%, 400,000 records processed, 3532 domains added, current time: 2024-11-04 13:05:28.227763, time per iteration: 1.250511 seconds
0.01%, 500,000 records processed, 4283 domains added, current time: 2024-11-04 13:05:29.589357, time per iteration: 1.361577 seconds
0.01%, 600,000 records processed, 4968 domains added, current time: 2024-11-04 13:05:30.849711, time per iteration: 1.260339 seconds
0.01%, 700,000 records processed, 5675 domains added, current time: 2024-11-04 13:05:32.121782, time per iteration: 1.272052 seconds
0.02%, 800,000 records processed, 6552 domains added, current time: 2024-11-04 13:05:33.531960, time per iteration: 1.410164 seconds
0.02%, 900,000 records processed, 7539 domains added, current time: 2024-11-04 13:05:34.930944, time per iteration: 1.39897 seconds
0.02%, 1,000,000 records processed, 8469 domains added, current time: 2024-11-04 13:05:36.313792, time per iteration: 1.382831 seconds
```


## Uncompressed file, simd json parser, deque with 1000 items
```
0.0%, 0 records processed, 0 domains added, current time: 2024-11-04 13:09:03.964716, time per iteration: 0.007081 seconds
0.0%, 100,000 records processed, 1090 domains added, current time: 2024-11-04 13:09:05.439390, time per iteration: 1.474662 seconds
0.0%, 200,000 records processed, 2177 domains added, current time: 2024-11-04 13:09:07.154014, time per iteration: 1.714611 seconds
0.01%, 300,000 records processed, 2882 domains added, current time: 2024-11-04 13:09:08.694328, time per iteration: 1.540298 seconds
0.01%, 400,000 records processed, 3532 domains added, current time: 2024-11-04 13:09:10.237280, time per iteration: 1.542939 seconds
0.01%, 500,000 records processed, 4283 domains added, current time: 2024-11-04 13:09:11.789491, time per iteration: 1.552195 seconds
0.01%, 600,000 records processed, 4968 domains added, current time: 2024-11-04 13:09:13.332267, time per iteration: 1.542762 seconds
0.01%, 700,000 records processed, 5675 domains added, current time: 2024-11-04 13:09:14.853697, time per iteration: 1.521413 seconds
0.02%, 800,000 records processed, 6552 domains added, current time: 2024-11-04 13:09:16.509664, time per iteration: 1.655954 seconds
0.02%, 900,000 records processed, 7539 domains added, current time: 2024-11-04 13:09:18.390420, time per iteration: 1.880743 seconds
0.02%, 1,000,000 records processed, 8469 domains added, current time: 2024-11-04 13:09:20.083775, time per iteration: 1.69334 seconds
```

## Uncompressed file, python json parser, no deque
```
0.0%, 0 records processed, 0 domains added, current time: 2024-11-04 13:10:37.119343, time per iteration: 0.006759 seconds
0.0%, 100,000 records processed, 1090 domains added, current time: 2024-11-04 13:10:38.471826, time per iteration: 1.352464 seconds
0.0%, 200,000 records processed, 2177 domains added, current time: 2024-11-04 13:10:39.904269, time per iteration: 1.432425 seconds
0.01%, 300,000 records processed, 2882 domains added, current time: 2024-11-04 13:10:41.127767, time per iteration: 1.223475 seconds
0.01%, 400,000 records processed, 3532 domains added, current time: 2024-11-04 13:10:42.279837, time per iteration: 1.152049 seconds
0.01%, 500,000 records processed, 4283 domains added, current time: 2024-11-04 13:10:43.453180, time per iteration: 1.173328 seconds
0.01%, 600,000 records processed, 4968 domains added, current time: 2024-11-04 13:10:44.611987, time per iteration: 1.158793 seconds
0.01%, 700,000 records processed, 5675 domains added, current time: 2024-11-04 13:10:45.809529, time per iteration: 1.197523 seconds
0.02%, 800,000 records processed, 6552 domains added, current time: 2024-11-04 13:10:47.056840, time per iteration: 1.247296 seconds
0.02%, 900,000 records processed, 7539 domains added, current time: 2024-11-04 13:10:48.376759, time per iteration: 1.319907 seconds
0.02%, 1,000,000 records processed, 8469 domains added, current time: 2024-11-04 13:10:49.666432, time per iteration: 1.289654 seconds
```

## No tldextract, uncompressed file, simd json parser, no deque
```
0.0%, 0 records processed, 0 domains added, current time: 2024-11-04 13:19:08.702165, time per iteration: 7.4e-05 seconds
0.0%, 100,000 records processed, 1565 domains added, current time: 2024-11-04 13:19:09.575101, time per iteration: 0.872927 seconds
0.0%, 200,000 records processed, 3076 domains added, current time: 2024-11-04 13:19:10.400112, time per iteration: 0.824992 seconds
0.01%, 300,000 records processed, 4216 domains added, current time: 2024-11-04 13:19:11.061182, time per iteration: 0.661053 seconds
0.01%, 400,000 records processed, 5301 domains added, current time: 2024-11-04 13:19:11.694815, time per iteration: 0.633618 seconds
0.01%, 500,000 records processed, 6512 domains added, current time: 2024-11-04 13:19:12.373475, time per iteration: 0.678646 seconds
0.01%, 600,000 records processed, 7606 domains added, current time: 2024-11-04 13:19:12.981620, time per iteration: 0.608131 seconds
0.01%, 700,000 records processed, 8721 domains added, current time: 2024-11-04 13:19:13.629914, time per iteration: 0.648279 seconds
0.02%, 800,000 records processed, 10081 domains added, current time: 2024-11-04 13:19:14.394792, time per iteration: 0.764865 seconds
0.02%, 900,000 records processed, 11602 domains added, current time: 2024-11-04 13:19:15.231544, time per iteration: 0.836738 seconds
0.02%, 1,000,000 records processed, 13006 domains added, current time: 2024-11-04 13:19:16.000511, time per iteration: 0.768952 seconds
Processed 1056791 domains in 7.710942 seconds. 137050.94 domains per second.
```

## no tldextract, skipping empty subdomains, simd json parser, no deque
```
0.0%, 0 records processed, 0 domains added, current time: 2024-11-04 13:31:10.700258, time per iteration: 9.3e-05 seconds
0.0%, 100,000 records processed, 1090 domains added, current time: 2024-11-04 13:31:11.486764, time per iteration: 0.786493 seconds
0.0%, 200,000 records processed, 2177 domains added, current time: 2024-11-04 13:31:12.144387, time per iteration: 0.657601 seconds
0.01%, 300,000 records processed, 2882 domains added, current time: 2024-11-04 13:31:12.644858, time per iteration: 0.500453 seconds
0.01%, 400,000 records processed, 3532 domains added, current time: 2024-11-04 13:31:13.109928, time per iteration: 0.465051 seconds
0.01%, 500,000 records processed, 4283 domains added, current time: 2024-11-04 13:31:13.614412, time per iteration: 0.504467 seconds
0.01%, 600,000 records processed, 4968 domains added, current time: 2024-11-04 13:31:14.083250, time per iteration: 0.468819 seconds
0.01%, 700,000 records processed, 5675 domains added, current time: 2024-11-04 13:31:14.567653, time per iteration: 0.484383 seconds
0.02%, 800,000 records processed, 6552 domains added, current time: 2024-11-04 13:31:15.121885, time per iteration: 0.554216 seconds
0.02%, 900,000 records processed, 7539 domains added, current time: 2024-11-04 13:31:15.738420, time per iteration: 0.61652 seconds
0.02%, 1,000,000 records processed, 8469 domains added, current time: 2024-11-04 13:31:16.338812, time per iteration: 0.600381 seconds
0.02%, 1,100,000 records processed, 9310 domains added, current time: 2024-11-04 13:31:16.948490, time per iteration: 0.609658 seconds
^CProcessing interrupted. Exiting...
Processed 1123777 domains in 6.39378 seconds. 175761 domains per second.
It will take 7.9 hours to process 4 billion records...
```

## some insert optimzations and fewer calles to datetime on insert
```
2024-11-04 13:34:27	INFO     - Ingesting file: merklemap_dns_records_database_25_10_2024.jsonl
0.0%, 0 records processed, 0 domains added, current time: 2024-11-04 13:34:27.234926, time per iteration: 7.6e-05 seconds
0.0%, 100,000 records processed, 1090 domains added, current time: 2024-11-04 13:34:27.894064, time per iteration: 0.659138 seconds
0.0%, 200,000 records processed, 2177 domains added, current time: 2024-11-04 13:34:28.547846, time per iteration: 0.653782 seconds
0.01%, 300,000 records processed, 2882 domains added, current time: 2024-11-04 13:34:29.033192, time per iteration: 0.485346 seconds
0.01%, 400,000 records processed, 3532 domains added, current time: 2024-11-04 13:34:29.492069, time per iteration: 0.458877 seconds
0.01%, 500,000 records processed, 4283 domains added, current time: 2024-11-04 13:34:29.992298, time per iteration: 0.500229 seconds
0.01%, 600,000 records processed, 4968 domains added, current time: 2024-11-04 13:34:30.455013, time per iteration: 0.462715 seconds
0.01%, 700,000 records processed, 5675 domains added, current time: 2024-11-04 13:34:30.931536, time per iteration: 0.476523 seconds
0.02%, 800,000 records processed, 6552 domains added, current time: 2024-11-04 13:34:31.517126, time per iteration: 0.58559 seconds
0.02%, 900,000 records processed, 7539 domains added, current time: 2024-11-04 13:34:32.144309, time per iteration: 0.627183 seconds
0.02%, 1,000,000 records processed, 8469 domains added, current time: 2024-11-04 13:34:32.713911, time per iteration: 0.569602 seconds
^CProcessing interrupted. Exiting...
Processed 1075906 domains in 5.898542 seconds. 182402 domains per second.
It will take 7.61 hours to process 4 billion records...
```

## all previous improvements + python 3.9 to 3.12 (highest simdjson supported)
```
2024-11-04 13:56:22	INFO     - Ingesting file: merklemap_dns_records_database_25_10_2024.jsonl
0.0%, 0 records processed, 0 domains added, current time: 2024-11-04 13:56:22.859731, time per iteration: 6.2e-05 seconds
0.0%, 100,000 records processed, 1090 domains added, current time: 2024-11-04 13:56:23.447485, time per iteration: 0.587754 seconds
0.0%, 200,000 records processed, 2177 domains added, current time: 2024-11-04 13:56:24.039830, time per iteration: 0.592345 seconds
0.01%, 300,000 records processed, 2882 domains added, current time: 2024-11-04 13:56:24.470904, time per iteration: 0.431074 seconds
0.01%, 400,000 records processed, 3532 domains added, current time: 2024-11-04 13:56:24.878175, time per iteration: 0.407271 seconds
0.01%, 500,000 records processed, 4283 domains added, current time: 2024-11-04 13:56:25.316732, time per iteration: 0.438557 seconds
0.01%, 600,000 records processed, 4968 domains added, current time: 2024-11-04 13:56:25.727740, time per iteration: 0.411008 seconds
0.01%, 700,000 records processed, 5675 domains added, current time: 2024-11-04 13:56:26.157411, time per iteration: 0.429671 seconds
0.02%, 800,000 records processed, 6552 domains added, current time: 2024-11-04 13:56:26.646042, time per iteration: 0.488631 seconds
0.02%, 900,000 records processed, 7539 domains added, current time: 2024-11-04 13:56:27.179809, time per iteration: 0.533767 seconds
0.02%, 1,000,000 records processed, 8469 domains added, current time: 2024-11-04 13:56:27.693472, time per iteration: 0.513663 seconds
^CProcessing interrupted. Exiting...
Processed 1135935 domains in 5.499674 seconds. 206546 domains per second.
It will take 6.72 hours to process 4 billion records...
```

## bulk buffered inserts in plaats van single trip per insert
```
2024-11-04 14:12:14	INFO     - Ingesting file: merklemap_dns_records_database_25_10_2024.jsonl
0.0%, 0 records processed, 0 domains added, current time: 2024-11-04 14:12:14.228161, time per iteration: 6.5e-05 seconds
0.0%, 100,000 records processed, 1090 domains added, current time: 2024-11-04 14:12:14.394804, time per iteration: 0.166643 seconds
0.0%, 200,000 records processed, 2177 domains added, current time: 2024-11-04 14:12:14.553830, time per iteration: 0.159026 seconds
0.01%, 300,000 records processed, 2882 domains added, current time: 2024-11-04 14:12:14.674980, time per iteration: 0.12115 seconds
0.01%, 400,000 records processed, 3532 domains added, current time: 2024-11-04 14:12:14.837796, time per iteration: 0.162816 seconds
0.01%, 500,000 records processed, 4283 domains added, current time: 2024-11-04 14:12:15.004170, time per iteration: 0.166374 seconds
0.01%, 600,000 records processed, 4968 domains added, current time: 2024-11-04 14:12:15.129123, time per iteration: 0.124953 seconds
0.01%, 700,000 records processed, 5675 domains added, current time: 2024-11-04 14:12:15.298834, time per iteration: 0.169711 seconds
0.02%, 800,000 records processed, 6552 domains added, current time: 2024-11-04 14:12:15.464973, time per iteration: 0.166139 seconds
0.02%, 900,000 records processed, 7539 domains added, current time: 2024-11-04 14:12:15.633784, time per iteration: 0.168811 seconds
0.02%, 1,000,000 records processed, 8469 domains added, current time: 2024-11-04 14:12:15.808219, time per iteration: 0.174435 seconds
^CProcessing interrupted. Exiting...
Processed 1703601 domains in 2.675813 seconds. 636668 domains per second.
It will take 2.18 hours to process 4 billion records...
```
