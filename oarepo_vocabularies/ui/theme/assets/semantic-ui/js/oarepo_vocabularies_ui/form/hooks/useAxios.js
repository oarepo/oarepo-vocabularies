import { useState, useEffect } from "react";
import { http } from "react-invenio-forms";

// axios.defaults.baseURL = 'https://jsonplaceholder.typicode.com';

export const useAxios = ({ url, method = "get", body = null }) => {
  const [response, setResponse] = useState(null);
  const [error, setError] = useState({});
  const [loading, setloading] = useState(true);

  const fetchData = () => {
    http[method](url, JSON.parse(body))
      .then((res) => {
        setResponse(res.data);
      })
      .catch((err) => {
        setError(err.response.data);
      })
      .finally(() => {
        setloading(false);
      });
  };

  useEffect(() => {
    fetchData();
  }, [method, url, body]);

  return { response, error, loading };
};
