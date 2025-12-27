CREATE TABLE Categories (
    CategoryID SERIAL PRIMARY KEY,
    CategoryName VARCHAR(100) NOT NULL,
    Description TEXT
);


CREATE TABLE Products (
    ProductID SERIAL PRIMARY KEY,
    ProductName VARCHAR(200) NOT NULL,
    Brand VARCHAR(100),
    Price DECIMAL(10,2) NOT NULL,
    Size VARCHAR(10),
    Color VARCHAR(50),
    IsAvailable BOOLEAN DEFAULT true,
    CategoryID INT NOT NULL,
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
);


CREATE TABLE Customers (
    CustomerID SERIAL PRIMARY KEY,
    FullName VARCHAR(150) NOT NULL,
    Email VARCHAR(100),
    Phone VARCHAR(20),
    RegistrationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    IsActive BOOLEAN DEFAULT true
);


CREATE TABLE Orders (
    OrderID SERIAL PRIMARY KEY,
    CustomerID INT NOT NULL,
    OrderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    TotalAmount DECIMAL(10,2) DEFAULT 0,
    Status VARCHAR(50) DEFAULT 'Новый',
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);


CREATE TABLE OrderItems (
    OrderItemID SERIAL PRIMARY KEY,
    OrderID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);


CREATE TABLE Stock (
    StockID SERIAL PRIMARY KEY,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL,
    LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);


INSERT INTO Categories (CategoryName, Description) VALUES 
('Футболки', 'Мужские и женские футболки'),
('Джинсы', 'Джинсовая одежда'),
('Куртки', 'Верхняя одежда');

INSERT INTO Products (ProductName, Brand, Price, Size, Color, IsAvailable, CategoryID) VALUES 
('Футболка базовая', 'Fashion', 1299.00, 'M', 'Белый', true, 1),
('Джинсы скинни', 'DenimPro', 3499.50, 'L', 'Синий', true, 2),
('Куртка демисезон', 'WarmWear', 7599.00, 'XL', 'Черный', true, 3);

INSERT INTO Customers (FullName, Email, Phone, IsActive) VALUES 
('Сидоров Алексей', 'alex@mail.ru', '89991234567', true),
('Кузнецова Мария', 'maria@mail.ru', '89997654321', true);

INSERT INTO Orders (CustomerID, TotalAmount, Status) VALUES 
(1, 4798.50, 'Оплачен'),
(2, 7599.00, 'Доставлен');

INSERT INTO OrderItems (OrderID, ProductID, Quantity, UnitPrice) VALUES 
(1, 1, 1, 1299.00),
(1, 2, 1, 3499.50),
(2, 3, 1, 7599.00);

INSERT INTO Stock (ProductID, Quantity) VALUES 
(1, 50),
(2, 30),
(3, 15);