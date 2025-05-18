import csv
from pathlib import Path
from config import (
    DATA_RAW,
    DATA_PROCESSED
)

def process_file(file_path, output_dir, max_lines=None):
    filename = Path(file_path).name
    quarter_code = filename.split(".")[2]  # e.g., '202206'
    yearquarter = quarter_code

    output_path = Path(output_dir) / f"filtered_las_q2_{yearquarter[:4]}.csv"
    written = 0

    header = [
        "TicketID", "UniqueCarrier", "YearQuarter", "CouponNum", "SequenceNum",
        "Origin", "OriginWAC", "Roundtrip", "FareClass",
        "SegmentNum", "MarketingCarrier", "OperatingCarrier",
        "Distance", "ArrivalAirport", "FareAmount"
    ]

    with open(file_path, "r") as infile, open(output_path, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)

        for i, line in enumerate(infile):
            if max_lines and i >= max_lines:
                break

            parts = line.strip().split("|")
            if len(parts) < 21:
                continue

            # Itinerary-level fields
            ticket_id      = parts[0]
            unique_carrier = parts[1]
            yq             = parts[2]
            coupon_num     = parts[3]
            sequence_num   = parts[4]
            origin         = parts[5]
            origin_wac     = parts[7]
            roundtrip      = parts[8]
            fare_class     = parts[9]

            if yq[:4] != yearquarter[:4]:
                continue

            # Loop through all flight segments in the record
            segment_start = 10
            segment_num = 1
            while segment_start + 10 < len(parts):
                seg = parts[segment_start:segment_start + 11]
                if len(seg) < 11:
                    break

                arrival_airport = seg[6]
                if arrival_airport != "LAS":
                    segment_start += 11
                    segment_num += 1
                    continue

                try:
                    distance = float(seg[5])
                    fare = float(seg[10])
                except ValueError:
                    distance = fare = None

                writer.writerow([
                    ticket_id, unique_carrier, yq, coupon_num, sequence_num,
                    origin, origin_wac, roundtrip, fare_class,
                    segment_num, seg[0], seg[2],
                    distance, arrival_airport, fare
                ])
                written += 1
                segment_start += 11
                segment_num += 1

    print(f"✅ {output_path.name}: {written} LAS-arrival segments exported.")


def process_all_files(folder_path=DATA_RAW, max_lines=None):
    path = Path(folder_path)
    files = sorted(path.glob("db1b.public.*.asc"))

    output_dir = Path(DATA_PROCESSED)
    output_dir.mkdir(exist_ok=True)

    for file in files:
        print(f"🔍 Processing: {file.name}")
        process_file(file, output_dir, max_lines=max_lines)


if __name__ == "__main__":
    process_all_files(".", max_lines=None)  # or max_lines=100000 for testing
