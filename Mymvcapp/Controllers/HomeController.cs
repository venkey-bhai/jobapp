using System;
using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;
using MyMvcApp.Models;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace MyMvcApp.Controllers;

public class HomeController : Controller
{
    private readonly HttpClient _httpClient;

    public HomeController(IHttpClientFactory httpClientFactory)
    {
        _httpClient = httpClientFactory.CreateClient("FastAPI");
    }

    public IActionResult Index()
    {
        return View();
    }

        
    public IActionResult Candidate()
    {
        
        return View();
    }

    public IActionResult PrivacyPolicy()
    {
        return View();
    }

    [HttpPost]
    public async Task<IActionResult> Candidate(
    string fullname,
    string gender,
    string email,
    string mobile,
    string position,
    string qualification,
    string experience,
    string yearOfPassing,
    string percentage,
    string college,
    string primarySkills,
    string secondarySkills,
    string languagesKnown,
    IFormFile resume)
    {
        Console.WriteLine($"Full Name: {fullname}");
        using var form = new MultipartFormDataContent();


        form.Add(new StringContent(fullname ?? ""), "fullname");
        form.Add(new StringContent(email ?? ""), "email");
         form.Add(new StringContent(gender ?? ""), "gender");
        form.Add(new StringContent(mobile ?? ""), "mobile");
        form.Add(new StringContent(position ?? ""), "position");
        form.Add(new StringContent(qualification ?? ""), "qualification");
        form.Add(new StringContent(experience ?? ""), "experience");
        form.Add(new StringContent(yearOfPassing ?? ""), "yearOfPassing");
        form.Add(new StringContent(percentage ?? ""), "percentage");
        form.Add(new StringContent(college ?? ""), "college");
        form.Add(new StringContent(primarySkills ?? ""), "primarySkills");
        form.Add(new StringContent(secondarySkills ?? ""), "secondarySkills");
        form.Add(new StringContent(languagesKnown ?? ""), "languagesKnown");
        // Upload resume
        if (resume != null && resume.Length > 0)
        {
            var fileContent =
                new StreamContent(resume.OpenReadStream());

            fileContent.Headers.ContentType =
                new System.Net.Http.Headers.MediaTypeHeaderValue(
                    resume.ContentType
                );

            form.Add(
                fileContent,
                "resume",
                resume.FileName
            );
        }


        // Send to FastAPI
        var response = await _httpClient.PostAsync(
            "students/upload_resume/",
            form
        );


        if (!response.IsSuccessStatusCode)
        {
            var error =
                await response.Content.ReadAsStringAsync();

            return Content(
                $"FastAPI Error: {error}"
            );
        }


        // Successfully saved
        return RedirectToAction("ViewCandidate");

    }

[HttpGet]
  public async Task<IActionResult> ViewCandidate()
{
    var response = await _httpClient.GetAsync("students");

    if (!response.IsSuccessStatusCode)
    {
        var errorMessage = await response.Content.ReadAsStringAsync();

        return Content(
            $"FastAPI Error: {(int)response.StatusCode} - {errorMessage}"
        );
    }

    var json = await response.Content.ReadAsStringAsync();

    var students = JsonSerializer.Deserialize<List<Student>>(
        json,
        new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        }
    );

    return View(students ?? new List<Student>());
}

    [ResponseCache(
        Duration = 0,
        Location = ResponseCacheLocation.None,
        NoStore = true
    )]
    public IActionResult Error()
    {
        return View(
            new ErrorViewModel
            {
                RequestId =
                    Activity.Current?.Id ??
                    HttpContext.TraceIdentifier
            }
        );
    }


[HttpPost]
public async Task<IActionResult> DeleteCandidate(string candidateId)
{
    try
    {
        var response = await _httpClient.DeleteAsync(
            $"students/{candidateId}/"
        );

        if (!response.IsSuccessStatusCode)
        {
            var error = await response.Content.ReadAsStringAsync();

            return Content(
                $"FastAPI Delete Error: {(int)response.StatusCode} - {error}"
            );
        }

        return RedirectToAction("ViewCandidate");
    }
    catch (Exception ex)
    {
        return Content(
            $"Error connecting to FastAPI: {ex.Message}"
        );
    }
}


[HttpGet]
public async Task<IActionResult> SearchCandidate(string search)
{
    var response = await _httpClient.GetAsync(
        $"students/search/{Uri.EscapeDataString(search ?? "")}/"
    );

    if (!response.IsSuccessStatusCode)
    {
        var error = await response.Content.ReadAsStringAsync();

        return Content(
            $"FastAPI Error: {(int)response.StatusCode} - {error}"
        );
    }

    var json = await response.Content.ReadAsStringAsync();

    var options = new JsonSerializerOptions
    {
        PropertyNameCaseInsensitive = true,
        NumberHandling = JsonNumberHandling.AllowReadingFromString
    };

    var students = JsonSerializer.Deserialize<List<Student>>(json, options);

    return View(
        "ViewCandidate",
        students ?? new List<Student>()
    );
}


[HttpGet]
public async Task<IActionResult> EditCandidate(string id)
{
    try
    {
        var response = await _httpClient.GetAsync("students");

        if (!response.IsSuccessStatusCode)
        {
            return View("Error");
        }

        var json = await response.Content.ReadAsStringAsync();
        var students = JsonSerializer.Deserialize<List<Student>>(
            json,
            new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            }
        );

        var candidate = students?.FirstOrDefault(c => c.Id == id);
        
        if (candidate == null)
        {
            return View("Error");
        }

        return View(candidate);
    }
    catch
    {
        return View("Error");
    }
}

[HttpPost]
public async Task<IActionResult> EditCandidate(string id, string status)
{
    try
    {
        var form = new FormUrlEncodedContent(new[]
        {
            new KeyValuePair<string, string>("status", status ?? "")
        });

        var response = await _httpClient.PutAsync(
            $"students/{Uri.EscapeDataString(id)}/",
            form
        );

        if (!response.IsSuccessStatusCode)
        {
            var error = await response.Content.ReadAsStringAsync();
            return Content(
                $"FastAPI Error: {(int)response.StatusCode} - {error}"
            );
        }

        return RedirectToAction("ViewCandidate");
    }
    catch (Exception ex)
    {
        return Content(
            $"Error connecting to FastAPI: {ex.Message}"
        );
    }
 }
    
}    
    





