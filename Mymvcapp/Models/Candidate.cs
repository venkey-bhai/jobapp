namespace MyMvcApp.Models
{
    public class Candidate
    {
        public int Id { get; set; }

        public string? fullname { get; set; }

        public string? email { get; set; }

        public string? mobile { get; set; }

        public string? gender { get; set; }

        public string? position { get; set; }

        public string? qualification { get; set; }

        public string? experience { get; set; }

        public int? yearOfPassing { get; set; }

        public float? percentage { get; set; }

        public string? college { get; set; }

        public string? primarySkills { get; set; }

        public string? secondarySkills { get; set; }

        public string? languagesKnown { get; set; }

        public string? resume { get; set; } 

        public DateTime? createdAt { get; set; }

        public string? status { get; set; }
    }
}