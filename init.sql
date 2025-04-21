CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    department VARCHAR(100) CHECK (department IN ('HR', 'Engineering', 'Marketing', 'Sales', 'Finance', 'IT', 'Operations')),
    salary DECIMAL(10,2) CHECK (salary > 0),
    hire_date DATE DEFAULT CURRENT_DATE
);

INSERT INTO employees (first_name, last_name, email, phone, department, salary, hire_date) VALUES
('John', 'Doe', 'john.doe@example.com', '9876543210', 'Engineering', 85000.00, '2023-06-15'),
('Jane', 'Smith', 'jane.smith@example.com', '9876543211', 'HR', 60000.00, '2022-09-22'),
('Alice', 'Brown', 'alice.brown@example.com', '9876543212', 'Marketing', 55000.00, '2021-11-10'),
('Bob', 'Johnson', 'bob.johnson@example.com', '9876543213', 'Sales', 70000.00, '2020-05-30'),
('Emma', 'Wilson', 'emma.wilson@example.com', '9876543214', 'Finance', 90000.00, '2019-02-18'),
('Liam', 'Anderson', 'liam.anderson@example.com', '9876543215', 'IT', 95000.00, '2021-03-14'),
('Olivia', 'Martinez', 'olivia.martinez@example.com', '9876543216', 'Operations', 78000.00, '2020-07-25'),
('Noah', 'Harris', 'noah.harris@example.com', '9876543217', 'Engineering', 88000.00, '2023-01-12'),
('Sophia', 'Clark', 'sophia.clark@example.com', '9876543218', 'HR', 62000.00, '2022-08-19'),
('Mason', 'Lewis', 'mason.lewis@example.com', '9876543219', 'Marketing', 57000.00, '2021-10-05');
ON CONFLICT DO NOTHING;