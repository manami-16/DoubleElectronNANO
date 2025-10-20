## 📘 About

The **`brilcalc/`** directory provides a convenient way to calculate the **integrated luminosity** (in `/fb`) for a given data-taking period using the CMS BRIL (Beam Radiation Instrumentation and Luminosity) framework.

All luminosity outputs are saved as CSV files under:
```
brilcalc/lumi_outputs/*.csv
```

### 💡 Example Terminal Output
```
Running: brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json -u /fb -i Cert_Collisions2022_355100_362760_Golden.json -o lumi_outputs/2022_G_lumi.csv --begin 362433 --end 362760

Warning: problems found in merging -i and --normtag selections:
  in run 359661 [[40, 232]] is not a superset of [[42, 233]]
Output saved to: lumi_outputs/2022_G_lumi.csv

Verifying lumi sums for 2022 G...
   📊 Calculated recorded sum: 3.082753035 /fb
   📄 Summary recorded value:  3.082753036 /fb
   🔍 Difference:              1.000000527e-09 (0.000%)
   ✅ Match (perfect or rounding-level).
```
### 🚀How to run `get_luminosity`?
#### 1. Edit [`runNum_era.yml`](https://github.com/manami-16/DoubleElectronNANO/blob/dev/brilcalc/runNum_era.yml)
```
2022: 
  Lumi: Cert_Collisions2022_355100_362760_Golden.json
  subera:
    C: [355862, 357482]
    D: [357538, 357900]
    E: [359022, 360331]
    F: [360390, 362167]
    G: [362433, 362760]

```
**Explanation:**
- **`Lumi`**: JSON file defining certified runs, downloadable from the [CMS Certification page](https://cms-service-dqmdc.web.cern.ch/CAF/certification/).
- **`subera`**: Specify the run ranges of interest in the format `[begin, end]`.
    - You can look up run numbers using [CMSDAS](https://cmsweb.cern.ch/das/).

#### 2. Download corresponding `*_Golden.json` under `brilcalc/` directory. 
Place the JSON file under your `brilcalc/` directory:
```
wget <link_to_json_file>
```
#### 3. Initialize your CMSSW by executing `cmsenv`
#### 4. Run the command `python3 get_luminosity.py`
- Output will be saved in `brilcalc/lumi_outputs/*.csv`
- Terminal output is still useful: 
```
Verifying lumi sums for 2022 G...
   📊 Calculated recorded sum: 3.082753035 /fb
   📄 Summary recorded value:  3.082753036 /fb
   🔍 Difference:              1.000000527e-09 (0.000%)
   ✅ Match (perfect or rounding-level).
```