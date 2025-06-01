import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getAllTours } from '../services/apiService';
import { TourReadClient } from '../types';

const ToursListPage: React.FC = () => {
  const [tours, setTours] = useState<TourReadClient[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTours = async () => {
      setIsLoading(true);
      try {
        const data = await getAllTours({ limit: 100 }); // Fetch more as needed
        setTours(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to fetch tours.');
        console.error('Fetch Tours Error:', err);
      }
      setIsLoading(false);
    };
    fetchTours();
  }, []);

  if (isLoading) return <p>Loading tours...</p>;
  if (error) return <p style={{ color: 'red' }}>Error: {error}</p>;

  return (
    <div style={{ padding: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h1>Manage Tours</h1>
        <Link to="/tours/create" style={{padding: '0.5rem 1rem', background: '#007bff', color: 'white', textDecoration: 'none', borderRadius: '4px'}}>
          Create New Tour
        </Link>
      </div>
      {tours.length === 0 ? (
        <p>No tours found.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={tableHeaderStyle}>Name</th>
              <th style={tableHeaderStyle}>Destination</th>
              <th style={tableHeaderStyle}>Start Date</th>
              <th style={tableHeaderStyle}>End Date</th>
              <th style={tableHeaderStyle}>Price</th>
              <th style={tableHeaderStyle}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {tours.map(tour => (
              <tr key={tour.id}>
                <td style={tableCellStyle}>{tour.name}</td>
                <td style={tableCellStyle}>{tour.destination}</td>
                <td style={tableCellStyle}>{new Date(tour.start_date).toLocaleDateString()}</td>
                <td style={tableCellStyle}>{new Date(tour.end_date).toLocaleDateString()}</td>
                <td style={tableCellStyle}>${tour.price_per_guest}</td>
                <td style={tableCellStyle}>
                  <Link to={`/tours/${tour.id}`} style={{ marginRight: '0.5rem' }}>View</Link>
                  {/* Edit/Delete links later */}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

const tableHeaderStyle: React.CSSProperties = {
  borderBottom: '2px solid #dee2e6',
  padding: '0.75rem',
  textAlign: 'left',
  background: '#f8f9fa'
};

const tableCellStyle: React.CSSProperties = {
  borderBottom: '1px solid #dee2e6',
  padding: '0.75rem',
};

export default ToursListPage;
