require("dotenv").config();
const express = require("express");
//const userRoutes = require("./routes/userRoutes");
const expenseRoutes = require("./routes/expenseRoute");
const estateRoutes = require("./routes/estateRoute");
const balanceRoutes = require("./routes/balanceRoute");
const healthRoutes = require("./routes/healthRoute");
const userRoutes = require("./routes/userRoute");

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true })); 
//각 테이블별 API 라우트 설정


//app.use("/users", userRoutes);
app.use("/estates", estateRoutes);
app.use("/expenses", expenseRoutes);
app.use("/balances", balanceRoutes);
app.use("/health", healthRoutes);
app.use("/users", userRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`🚀 서버 실행 중`));