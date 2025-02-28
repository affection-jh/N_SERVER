const express = require("express");
const db = require("../db/db");
const router = express.Router();

// DB 상태 확인
router.get("/", (req, res) => {
    db.ping((err) => {
      if (err) {
        return res.status(500).json({ status: "error", message: "DB 연결 실패" });
      }
      res.json({ status: "ok", message: "서버 및 DB 정상 작동" });
    });
  });
  module.exports = router;