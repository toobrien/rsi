from json import loads, dumps

SUMMARY_PATH = "./data/results/summary.json"
TABLE_PATH = "./data/results/table.md"
WIDTH = 15
HEADERS = [
    "group", "type", "enter", "exit", 
    "samples", "mae", "mfe", "pnl", 
    "duration"
]

with open(SUMMARY_PATH, "r") as fd:
    records = [ 
        "|".join(HEADERS),
        "|".join([ "-" * WIDTH for header in HEADERS ])
    ]
    summary = loads(fd.read())
    

    for record in summary:
        values = []
        values.append(record["test"]["group"])
        values.append(str(record["test"]["type"]))
        values.append(str(record["test"]["enter"]))
        values.append(str(record["test"]["exit"]))
        values.append(str(record["test"]["samples"]))
        for statistic in [ "mae", "mfe", "pnl"]:
            values.append(", ".join((
                str(record[statistic]["mean"]),
                str(record[statistic]["stdev"]),
                str((
                    record[statistic]["interval"]["lower"],
                    record[statistic]["interval"]["upper"]
                ))
            )))
        values.append(", ".join((
            str(record["duration"]["mean"]),
            str(record["duration"]["mean"])
        )))
        #print(dumps(values, indent = 2))
        records.append("|".join(values))
    
    with open(TABLE_PATH, "w") as fd:
        fd.write("\n".join(records))

