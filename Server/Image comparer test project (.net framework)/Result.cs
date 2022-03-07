using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Image_comparer_test_project__.net_framework_
{
    public partial class Result : Form
    {
        private Bitmap image;
        public Result()
        {
            InitializeComponent();
        }

        private void Result_Load(object sender, EventArgs e)
        {

        }

        public Bitmap Image {

            get => image; 

            set
            {
                image = value;
                pictureBox1.Image = image;
                //int verhouding = image.Width / image.Height;
                //pictureBox1.Size = new Size(1140, 1140 / verhouding);
                pictureBox1.Update();
            } 
        }

        private void pictureBox1_Click(object sender, EventArgs e)
        {

        }
    }
}
