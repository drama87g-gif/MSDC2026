using System;
using System.Windows.Forms;
using Microsoft.EntityFrameworkCore;
using Core.Data;

namespace AdminApp
{
    internal static class Program
    {
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            var conn = Environment.GetEnvironmentVariable("DATABASE_CONNECTION");
            if (string.IsNullOrWhiteSpace(conn))
            {
                MessageBox.Show("DATABASE_CONNECTION environment variable is required.", "Config error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            var options = new DbContextOptionsBuilder<MainDbContext>()
                .UseSqlServer(conn)
                .Options;

            try
            {
                using var db = new MainDbContext(options);
                db.Database.OpenConnection();
                db.Database.CloseConnection();
            }
            catch (Exception ex)
            {
                MessageBox.Show("DB connection failed: " + ex.Message, "DB error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            MessageBox.Show("DB OK. Starting Admin app (skeleton).", "Admin", MessageBoxButtons.OK, MessageBoxIcon.Information);
            // TODO: Launch main form
        }
    }
}
