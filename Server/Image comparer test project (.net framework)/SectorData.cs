using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Image_comparer_test_project__.net_framework_
{
    internal struct SectorData
    {
        public List<(int, int, int)> HSVData { get; set; }

        public string FileName { get; set; }
    }

    internal struct Results
    {
        public int HueDifference { get; set; }

        public int BrightnessDifference { get; set; }

        public int SaturationDifference { get; set; }

        public string FileName { get; set; }

        public string HueDiffPercent { get; set; }

        public string BrightnessDiffPercent { get; set; }

        public string SaturationDiffPercent { get; set; }
    }
}
