import csv
from pathlib import Path
from config import DATA_RAW, DATA_PROCESSED


HEADER = [
    "TicketID",
    "UniqueCarrier",
    "YearQuarter",
    "CouponNum",
    "SequenceNum",
    "Origin",
    "OriginWAC",
    "Roundtrip",
    "FareClass",
    "SegmentNum",
    "MarketingCarrier",
    "OperatingCarrier",
    "Distance",
    "ArrivalAirport",
    "FareAmount",
]


def process_file(file_path, writer, max_lines=None):
    filename = Path(file_path).name
    quarter_code = filename.split(".")[2]  # e.g., '202206'
    yearquarter = quarter_code
    written = 0
    rows = []

    with open(file_path, "r") as infile:
        for i, line in enumerate(infile):
            if max_lines and i >= max_lines:
                break

            parts = line.strip().split("|")
            if len(parts) < 21:
                continue

            # Itinerary-level fields
            ticket_id = parts[0]
            unique_carrier = parts[1]
            yq = parts[2]
            coupon_num = parts[3]
            sequence_num = parts[4]
            origin = parts[5]
            origin_wac = parts[7]
            roundtrip = parts[8]
            fare_class = parts[9]

            if yq[:4] != yearquarter[:4]:
                continue

            # Loop through all flight segments in the record
            total_segments = (len(parts) - 10) // 11
            for segment_num in range(1, total_segments + 1):
                segment_start = 10 + (segment_num - 1) * 11
                seg = parts[segment_start : segment_start + 11]
                if len(seg) < 11:
                    continue

                arrival_airport = seg[6]
                if segment_num != total_segments or arrival_airport != "LAS":
                    continue

                try:
                    distance = float(seg[5])
                    fare = float(seg[10])
                except ValueError:
                    distance = fare = None

                rows.append(
                    [
                        ticket_id,
                        unique_carrier,
                        yq,
                        coupon_num,
                        sequence_num,
                        origin,
                        origin_wac,
                        roundtrip,
                        fare_class,
                        segment_num,
                        seg[0],
                        seg[2],
                        distance,
                        arrival_airport,
                        fare,
                    ]
                )
                written += 1

    writer.writerows(rows)
    print(f"✅ {file_path.name}: {written} LAS-arrival segments appended.")


def get_flight_raw_data(folder_path=DATA_RAW, max_lines=None):
    path = Path(folder_path)
    files = sorted(path.glob("db1b.public.*.asc"))

    if not files:
        print("No files found.")
        return []

    all_rows = []
    for file in files:
        print(f"🔍 Processing: {file.name}")
        all_rows.extend(process_file(file, max_lines=max_lines))

    return all_rows


if __name__ == "__main__":
    # Exemplo de uso para teste, se necessário
    raw_data = get_flight_raw_data(".", max_lines=100000)
    output_dir = Path(DATA_PROCESSED)
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "filtered_las_raw_test.csv"
    with open(output_path, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(HEADER)
        writer.writerows(raw_data)
    print(f"Dados brutos de voos salvos para teste em: {output_path}")
