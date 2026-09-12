using Microsoft.AspNetCore.Mvc;
using MyMvcApp.Models;
using System.Text.Json;

namespace MyMvcApp.Controllers
{
    public class CandidatesController : Controller
    {
        private readonly HttpClient _httpClient;

        public CandidatesController(IHttpClientFactory httpClientFactory)
        {
            _httpClient = httpClientFactory.CreateClient();
        }

        public async Task<IActionResult> candidate()
        {
            var response = await _httpClient.GetAsync(
                "http://127.0.0.1:8000/students/"
            );

            if (!response.IsSuccessStatusCode)
            {
                return View("Error");
            }

            var json = await response.Content.ReadAsStringAsync();

            var candidates = JsonSerializer.Deserialize<List<Student>>(
                json,
                new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                }
            );

            return View(candidates ?? new List<Student>());
        }
    }
}