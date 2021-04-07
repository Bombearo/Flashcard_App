-- phpMyAdmin SQL Dump
-- version 5.0.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 07, 2021 at 12:10 PM
-- Server version: 10.4.14-MariaDB
-- PHP Version: 7.4.11

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `app`
--
CREATE DATABASE IF NOT EXISTS `app` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `app`;

-- --------------------------------------------------------

--
-- Table structure for table `app_user`
--

CREATE TABLE `app_user` (
  `userID` int(11) NOT NULL,
  `username` varchar(20) NOT NULL,
  `password` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `app_user`
--

INSERT INTO `app_user` (`userID`, `username`, `password`) VALUES
(1, 'Admin', 'AdminPass');

-- --------------------------------------------------------

--
-- Table structure for table `flashcard`
--

CREATE TABLE `flashcard` (
  `cardID` int(11) NOT NULL,
  `phrase` varchar(30) NOT NULL,
  `definition` varchar(100) NOT NULL,
  `setID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `flashcard`
--

INSERT INTO `flashcard` (`cardID`, `phrase`, `definition`, `setID`) VALUES
(147, 'uintathere', 'extinct Pleistocene hoofed herbivore', 32),
(148, 'xerasia', 'abnormal dryness of the hair', 32),
(149, 'mantic', 'of, like or pertaining to divination; prophetic; divinely inspired', 32),
(150, 'jalousie', 'outside shutter with slats', 32);
-- --------------------------------------------------------

--
-- Table structure for table `flashcard_set`
--

CREATE TABLE `flashcard_set` (
  `setID` int(11) NOT NULL,
  `setName` varchar(30) NOT NULL,
  `userID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `flashcard_set`
--

INSERT INTO `flashcard_set` (`setID`, `setName`, `userID`) VALUES
(32, 'English', 1);

-- --------------------------------------------------------

--
-- Table structure for table `user_sets`
--

CREATE TABLE `user_sets` (
  `setID` int(11) NOT NULL,
  `userID` int(11) NOT NULL,
  `nickname` varchar(30) DEFAULT NULL,
  `score` int(11) DEFAULT NULL CHECK (`score` <= 100 and `score` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `user_sets`
--

--
-- Indexes for dumped tables
--

--
-- Indexes for table `app_user`
--
ALTER TABLE `app_user`
  ADD PRIMARY KEY (`userID`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `flashcard`
--
ALTER TABLE `flashcard`
  ADD PRIMARY KEY (`cardID`),
  ADD KEY `setID` (`setID`);

--
-- Indexes for table `flashcard_set`
--
ALTER TABLE `flashcard_set`
  ADD PRIMARY KEY (`setID`),
  ADD KEY `userID` (`userID`);

--
-- Indexes for table `user_sets`
--
ALTER TABLE `user_sets`
  ADD PRIMARY KEY (`setID`,`userID`),
  ADD KEY `userID` (`userID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `app_user`
--
ALTER TABLE `app_user`
  MODIFY `userID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `flashcard`
--
ALTER TABLE `flashcard`
  MODIFY `cardID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=155;

--
-- AUTO_INCREMENT for table `flashcard_set`
--
ALTER TABLE `flashcard_set`
  MODIFY `setID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `flashcard`
--
ALTER TABLE `flashcard`
  ADD CONSTRAINT `flashcard_ibfk_1` FOREIGN KEY (`setID`) REFERENCES `flashcard_set` (`setID`);

--
-- Constraints for table `flashcard_set`
--
ALTER TABLE `flashcard_set`
  ADD CONSTRAINT `flashcard_set_ibfk_1` FOREIGN KEY (`userID`) REFERENCES `app_user` (`userID`);

--
-- Constraints for table `user_sets`
--
ALTER TABLE `user_sets`
  ADD CONSTRAINT `user_sets_ibfk_1` FOREIGN KEY (`setID`) REFERENCES `flashcard_set` (`setID`),
  ADD CONSTRAINT `user_sets_ibfk_2` FOREIGN KEY (`userID`) REFERENCES `app_user` (`userID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
