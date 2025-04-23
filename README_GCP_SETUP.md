# 🔐 Airflow GCP Setup Guide for IS3107 Project

If you're working on this project and require access to our Google Cloud resources, please contact the owners of this GitHub repository to obtain the required service account key file.

---

## ✅ Step-by-Step: Set Up Google Cloud Connection in Airflow

To run this project and interact with Google Cloud Storage, follow these steps to configure the Airflow GCP connection on your machine.

### 1. Launch Airflow UI
Open your browser and go to your local Airflow instance (usually at `http://localhost:8080`).

### 2. Add a New GCP Connection
- Go to **Admin → Connections**
- Click **“+ Add”** (top right)

### 3. Fill in the Connection Details:

| Field            | Value                                                                 |
|------------------|-----------------------------------------------------------------------|
| **Conn Id**       | `google_cloud_default`                                                |
| **Conn Type**     | `Google Cloud`                                                       |
| **Project ID**    | `is3107-project-457501`                                               |
| **Keyfile JSON**  | Open the `is3107-project-457501-4f502924c0f9.json` file in a text editor, copy everything, and paste it here |
| **Keyfile Path**  | *(Leave this blank)*                                                  |
| **Scopes**        | *(Leave this blank)*                                                  |

Then click **Save ✅**

> 💡 If you do not have the required `.json` file, contact a project owner to request access.

---

## 🚫 DO NOT

- ❌ Upload the `.json` file to any public or private GitHub repository
- ❌ Share it in public folders or forums

---

## ✅ You're Done!

Once the connection is set up, you'll be able to run the DAG and access our datasets on Google Cloud Storage automatically.

If you encounter permission issues, reach out to the project team.

---

*IS3107 Project Group*